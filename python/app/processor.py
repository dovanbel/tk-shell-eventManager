import datetime
import sgtk
from collections import defaultdict

def timeTree(): return defaultdict(timeTree)

class sg_Event(object) :
    

    def __init__(self, event_datetime, event_context, event_type, thisProject = True, db_id = None  ) :
        self.removeTime = []
        self.isLast_sc  = None 
        self.isFirst_sc = None
        self.db_id = db_id

        self.isCount = ""

        self.when        = event_datetime
        self.context     = event_context
        self.thisProject = thisProject 

        self.longType = event_type

        #'version_up','save_file_as', 'open_file', 'file_publish'
        if self.longType in ['new_file']:
            self.type = "n"
        if self.longType in ['open_file', 'open_file_snapshot']:
            self.type = "o"
        elif self.longType in ['version_up', 'save_file_as', 'save_file_snapshot']:
            self.type = "s"
        elif self.longType in ['file_publish']:
            self.type = "p"

    def __sub__(self, other) :
        
        if self.when.date() != other.when.date():
            return 0.0

        else :
            delta =  self.when - other.when 
            return (delta.seconds + delta.microseconds/1E6)/60.0



class event_filter(object) :

    def __init__(self,  timeIn = datetime.time(12,30,00), timeOut = datetime.time(15,00,00), timeRem=datetime.time(0,45,0) , timeInactivity=datetime.time(1,0,0), context="all", color = "#4444BB" ):
        self.color   = color
        self.timeIn  = timeIn
        self.timeOut = timeOut
        self.deltaRem = datetime.timedelta(hours=timeRem.hour, minutes=timeRem.minute, seconds=timeRem.second)

        self.deltaInactivity = datetime.timedelta(hours=timeInactivity.hour, minutes=timeInactivity.minute, seconds=timeInactivity.second)

        self.contextName = context

    def calculate(self, event, nextEvent):
        # is matching the inactivityTime ?

        # event-nextEvent

        if event.when.date() != nextEvent.when.date():
            return 0.0

        ina = ""
        # this two events do not match the filters inactivity duration          
        if (nextEvent-event) < (self.deltaInactivity.seconds/60.0) :    
            return 0.0
        else :

            ina = "ina :" +str((nextEvent-event)) +" sup "+ str(self.deltaInactivity.seconds/60.0)  + " IN : " + str(event.when.time() ) + " OUT : " + str(nextEvent.when.time() )


        if self.contextName != "all" :
            if event.context["name"] != self.contextName :
                return 0.0


        if self.timeIn <= event.when.time() and event.when.time() < self.timeOut :

            if  nextEvent.when.time() <= self.timeOut : 
                # ces deux evenement sont contenus dans les bornes du filtres
                return ( -1 * (self.deltaRem.seconds/60) )
            if nextEvent.when.time() > self.timeOut :
                minutes = self.durationBetweenTwoTimes(  event.when.time(),self.timeOut)
                if minutes >= (self.deltaInactivity.seconds/60.0) :
                    return ( -1 * (self.deltaRem.seconds/60) )

        return 0.0


    def durationBetweenTwoTimes(self, time1, time2):
        in1 = datetime.datetime.combine(datetime.date(1,1,1), time1) 
        in2 = datetime.datetime.combine(datetime.date(1,1,1), time2)  
        return ((in1-in2).seconds)/60.0

def get_contextList(dailyEventQueue) :
    """ 
        Parse a Queue of daily user events
        return the list of all differents contexts from which an event has been sent by the user... 

        In     : 
        - DailyEventQueue : sg_Event list
    
        return : 
        - List

    """

    contextList = []
    for event in dailyEventQueue :
        if not event.context in contextList :
            contextList.append(event.context)

    return contextList



def makeArray(  dailyEventQueue, contextList,  ) :

    array_2D=[]

    for event in dailyEventQueue :
        array_1D = []
        
        for context in contextList :
            if event.context == context :
                array_1D.append(event)
            else :
                array_1D.append(None) 
            
        array_2D.append(array_1D)


    return array_2D

def getTimeDelta(array_2D, idx) :
    if idx == 0 :
        return 0.0
    else :
        i = None
        j = None
        for i in array_2D[idx] :
            if i :
                break
        for j in array_2D[idx-1] :
            if j :
                break

        return i-j


def drawArray(array_2D, filterList, command ):
    consol = sgtk.platform.current_bundle().engine.log_info
    idx = 0
    prevDay = None
    for array_1D in array_2D :
        newA = []
        event = None
        
        for i in array_1D :
    
            if not i :
                newA.append("  -")
            else :
                event = i
                if not i.thisProject :
                    newA.append("<font color='#CCAAAA'>"+ i.type.rjust(3)+"</font>") 
                elif i.isLast_sc and i.isFirst_sc :
                    newA.append("<font color='#DD7777'>"+ i.type.rjust(3) + "</font>") 
                elif i.isLast_sc :
                    newA.append("<font color='#77DD77'>"+ i.type.rjust(3) + "</font>")                
                elif i.isFirst_sc :
                    newA.append("<font color='#7777DD'>"+ i.type.rjust(3) + "</font>")
                else :
                    newA.append( i.type.rjust(3) )
 

        daystr = "" 
        if event.when.day != prevDay :
            prevDay = event.when.day
            daystr = str("%03d" %event.when.day).ljust(4)
        else :
            daystr = "<font color='#BBBBBB'>"+str("%03d" %event.when.day).ljust(4)+"</font>"

        removeTimeStr =""
        
        #command("----->"+str(event.removeTime))
        for filterIdx in range(len(event.removeTime)) :
            if event.removeTime[filterIdx] != 0 :
                removeTimeStr+= "<font color='"+filterList[filterIdx].color+"'>"+str(event.removeTime[filterIdx])+"</font>  "
        
        strContext = event.context["name"]
        command(  str(event.db_id) +"  " + daystr + "->"+  "".join(newA) + "  " + str(event.when.time()) + "     " + "%5.2f"%float(str(getTimeDelta(array_2D, idx))[0:5])  + "  " + event.isCount.ljust(4) +"  " + strContext.ljust(15)+ "  " +removeTimeStr )
        idx+=1

    command ("\n")



def getNextEvent(array_2D, idx) :
    if (idx+1) >= len(array_2D) :
        return None
    
    for sg_event in array_2D[idx+1] :
        if sg_event :
            return sg_event

    return sg_event 

def getNextEvent_sameContext(array_2D, idx) :
    sg_event = None
    for sg_event in array_2D[idx] :
        if sg_event :
            for next_idx in range(idx+1, len(array_2D)):
                for next_sg_event in array_2D[next_idx] :
                    if next_sg_event :
                        if next_sg_event.context == sg_event.context :
                            if next_sg_event.when.date() == sg_event.when.date() : # same context, same day, same month, same year !
                                sg_event.isLast_sc = False
                                return sg_event, next_sg_event 
                            else :
                                sg_event.isLast_sc = True
                                return sg_event, None
            break
    sg_event.isLast_sc = True
    return sg_event, None

def getPrevEvent_sameContext(array_2D, idx) :
    for sg_event in array_2D[idx] :
        if sg_event :
            for prev_idx in range(0, idx)[::-1]:
                for prev_sg_event in array_2D[prev_idx] :
                    if prev_sg_event :
                        if prev_sg_event.context == sg_event.context :
                            if prev_sg_event.when.date() == sg_event.when.date() :  # same context, same day, same month, same year !
                                sg_event.isFirst_sc = False
                                return sg_event, prev_sg_event 
                            else :
                                sg_event.isFirst_sc = True
                                return sg_event, None
            break
    sg_event.isFirst_sc = True
    return sg_event, None


def doFilterCalcul(event, nextEvent, eventFilter_List) :
    consol = sgtk.platform.current_bundle().engine.log_info
    for ev_filt in eventFilter_List :
        timeRem = ev_filt.calculate( event, nextEvent)
        event.removeTime.append(timeRem)



    return event

def do_sum_filterArrayRemoveTime(sum_timeRemArray, timeRemArray ):

    new_sum_timeRemArray=[]

    isEmpty = False 
    if not len(sum_timeRemArray) :
        isEmpty = True


    for idx in range(len(timeRemArray)) :

        if isEmpty :
            new_sum_timeRemArray.append(timeRemArray[idx])
        else :  
            new_sum_timeRemArray.append(sum_timeRemArray[idx] + timeRemArray[idx])


    return new_sum_timeRemArray

def calculateArray(array_2D, contextList, eventFilter_List, command) :
    consol = sgtk.platform.current_bundle().engine.log_info
    dayContext_timeTree    = timeTree()

    emptyFilterArray = []
    for n in range(len(eventFilter_List)) :
        emptyFilterArray.append(0.0)



    for idx in range(len(array_2D)) :
         
        event , nextEvent_sc = getNextEvent_sameContext(array_2D, idx)

        nextEvent = getNextEvent(array_2D, idx)


        if nextEvent :

            # le cas AA
            if event.context  ==  nextEvent.context and event.thisProject : 
                
                prevBrut = dayContext_timeTree[str(event.when.date())][str(event.context)]["brut"]
                if type(defaultdict()) == type(prevBrut) :
                    dayContext_timeTree[str(event.when.date())][str(event.context)]["brut"]  = nextEvent-event
                else :
                    dayContext_timeTree[str(event.when.date())][str(event.context)]["brut"]  = prevBrut + ( nextEvent-event )
                
                prevTime = dayContext_timeTree[str(event.when.date())][str(event.context)]["calculated"]
                if type(defaultdict()) == type(prevTime) :
                    dayContext_timeTree[str(event.when.date())][str(event.context)]["calculated"]  = nextEvent-event
                else :
                    dayContext_timeTree[str(event.when.date())][str(event.context)]["calculated"]  = prevTime + ( nextEvent-event )
                

                timeRemArray = dayContext_timeTree[str(event.when.date())][str(event.context)]["filtered"]
                if type(defaultdict()) == type(timeRemArray) :
                    dayContext_timeTree[str(event.when.date())][str(event.context)]["filtered"] = emptyFilterArray
                else :
                    dayContext_timeTree[str(event.when.date())][str(event.context)]["filtered"] = do_sum_filterArrayRemoveTime(timeRemArray, emptyFilterArray)
                
                event.isCount+="AA "
                    
            # le cas AB
            else :
                if not event.isLast_sc :
                    if event.thisProject :
                        
                        prevBrut = dayContext_timeTree[str(event.when.date())][str(event.context)]["brut"]
                        if type(defaultdict()) == type(prevBrut) :
                            dayContext_timeTree[str(event.when.date())][str(event.context)]["brut"]  = nextEvent-event
                        else :
                            dayContext_timeTree[str(event.when.date())][str(event.context)]["brut"]  = prevBrut + ( nextEvent-event )
                        
                        if not nextEvent_sc.type in ["n","o"] :
                            event.isCount+="Ab+ "
                            # measured time goes to A                    
                            prevTime = dayContext_timeTree[str(event.when.date())][str(event.context)]["calculated"]
                            if type(defaultdict()) == type(prevTime) :
                                dayContext_timeTree[str(event.when.date())][str(event.context)]["calculated"]  = nextEvent-event
                            else :
                                dayContext_timeTree[str(event.when.date())][str(event.context)]["calculated"]  = prevTime + ( nextEvent-event )
                            
                            event =  doFilterCalcul(event, nextEvent, eventFilter_List)
                            timeRemArray = dayContext_timeTree[str(event.when.date())][str(event.context)]["filtered"]
                            if type(defaultdict()) == type(timeRemArray) :
                                dayContext_timeTree[str(event.when.date())][str(event.context)]["filtered"] = event.removeTime
                            else :
                                dayContext_timeTree[str(event.when.date())][str(event.context)]["filtered"] = do_sum_filterArrayRemoveTime(timeRemArray, event.removeTime)
                    
                        else :                 
                            event.isCount+="Ab0 "
                            prevTime = dayContext_timeTree[str(event.when.date())][str(event.context)]["calculated"]
                            if type(defaultdict()) == type(prevTime) :
                                dayContext_timeTree[str(event.when.date())][str(event.context)]["calculated"]  = 0.0
                            else :
                                dayContext_timeTree[str(event.when.date())][str(event.context)]["calculated"]  = prevTime + 0.0
                            

                            timeRemArray = dayContext_timeTree[str(event.when.date())][str(event.context)]["filtered"]
                            if type(defaultdict()) == type(timeRemArray) :
                                dayContext_timeTree[str(event.when.date())][str(event.context)]["filtered"] = emptyFilterArray
                            else :
                                dayContext_timeTree[str(event.when.date())][str(event.context)]["filtered"] = do_sum_filterArrayRemoveTime(timeRemArray, emptyFilterArray )
                
                else :
                    nextEvent , prevEvent_sc = getPrevEvent_sameContext(array_2D, idx+1)

                    if nextEvent.thisProject :
                        prevBrut = dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["brut"]
                        if type(defaultdict()) == type(prevBrut) :
                            dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["brut"]  = nextEvent-event
                        else :
                            dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["brut"]  = prevBrut + ( nextEvent-event )
                        


                        if prevEvent_sc :
                            nextEvent.isCount+="aB+ "
                            prevTime = dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["calculated"]
                            if type(defaultdict()) == type(prevTime) :
                                dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["calculated"]  = nextEvent-event
                            else :
                                dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["calculated"]  = prevTime + ( nextEvent-event )
                            
                            event = doFilterCalcul(event, nextEvent, eventFilter_List)
                            timeRemArray = dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["filtered"]
                            if type(defaultdict()) == type(timeRemArray) :
                                dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["filtered"] = event.removeTime
                            else :
                                dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["filtered"] = do_sum_filterArrayRemoveTime(timeRemArray, event.removeTime)
                   

                        else :
                            nextEvent.isCount+="aB0 "
                            prevTime = dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["calculated"]
                            if type(defaultdict()) == type(prevTime) :
                                dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["calculated"]  = 0.0
                            else :
                                dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["calculated"]  = prevTime + 0.0
                            

                            timeRemArray = dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["filtered"]


                            if type(defaultdict()) == type(timeRemArray) :
                                dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["filtered"] = emptyFilterArray
                            else :
                                dayContext_timeTree[str(nextEvent.when.date())][str(nextEvent.context)]["filtered"] = do_sum_filterArrayRemoveTime(timeRemArray, emptyFilterArray )






        idx += 1

    return dayContext_timeTree


def preLaunch(progressBar, logLabel, app) :
    
    progressBar.setFormat("Querying shotgun project task names")
    stepProgressBar = 0 
    progressBar.setValue(stepProgressBar)

    sg = app.engine.tank.shotgun

    #projectId = {"type":'Project',"id":186} # app.context.project)
    projectId = app.context.project
    
    eventFilterList = ['version_up','save_file_as', 'open_file', 'file_publish', 'new_file','open_file','open_file_snapshot' ]
    filters = [ ["project", "is", projectId],  ["event_type", "in", eventFilterList ], ["entity", 'is_not', None]  ]
    eventsList = sg.find("EventLogEntry", filters, [ "entity"] )

    entityList = []
    for event in eventsList :

        if not event["entity"]["name"] in entityList :
            #sgtk.platform.current_bundle().engine.log_info(str(event["entity"]["name"]))
            entityList.append(event["entity"]["name"])

        stepProgressBar += 100/len(eventsList)
        progressBar.setValue(stepProgressBar)


    progressBar.setFormat("startup completed")
    progressBar.setValue(stepProgressBar)
    return sorted(entityList)




def displayDataWS(workstationDict, cout ):
    """
    for workstation in workstationDict.keys():
        cout(workstation)
    """
def displayDataContext(workstationDict, cout ):
    consol = sgtk.platform.current_bundle().engine.log_info

    dataContextDict=dict()
    
    for ws in workstationDict.keys():
        value = 0
        for day in workstationDict[ws].keys() :

            for context in workstationDict[ws][day].keys():
                
                calculatedValue = workstationDict[ws][day][context]["calculated"]
                filteredValue = workstationDict[ws][day][context]["filtered"]
                brutValue = workstationDict[ws][day][context]["brut"]

                contextDict = None
                exec("contextDict=%s"%context)


                if dataContextDict.has_key(str(contextDict["name"]) ) :
                    dataContextDict[str(contextDict["name"]) ]["calculated"]     += calculatedValue
                    sum_removeTimeArray = dataContextDict[str(contextDict["name"]) ]["filtered"]
                    dataContextDict[str(contextDict["name"]) ]["filtered"] = do_sum_filterArrayRemoveTime(  sum_removeTimeArray, filteredValue)
                    dataContextDict[str(contextDict["name"]) ]["brut"] += brutValue
                else :
                    dataContextDict[str(contextDict["name"]) ] = {"calculated": calculatedValue,"filtered" : filteredValue, "brut" : brutValue}

    fullCalculated = 0
    fullNet = 0
    fullBruteTime = 0

    for context in dataContextDict.keys():
        cout(context)
        calculated = dataContextDict[context]["calculated"]
        brut = dataContextDict[context]["brut"]
        
        cout("  Filtered : " +  str(dataContextDict[context]["filtered"]) )
        sumFiltered  = 0
        for filterValue in dataContextDict[context]["filtered"]:
            sumFiltered  += filterValue
        
        

        net = calculated + sumFiltered
        
        
        cout("  brut : " + formatMinutes(brut))
        cout("  calculated : "  +  formatMinutes(calculated)) # str(round(brut,2 ) ) )
        cout("  Net : "   +  formatMinutes(net)) # str(round(net,2) ) ) 
        cout("  Ratio calculated = " + str(round(calculated/brut*100,2) ) + " % brut" )
        cout("  Ratio net = " + str(round(net/brut*100,2) ) + " % brut = " + str(round(net/calculated*100,2) ) + " % calculated")

        fullCalculated += calculated
        fullNet += net
        fullBruteTime += brut



    cout("\n####### TOTALS ########")
    cout("brut       : " + formatMinutes(fullBruteTime))
    cout("calculated : " + formatMinutes(fullCalculated))
    cout("net        : " + formatMinutes(fullNet))
    cout("Ratio calculated = " + str(round(fullCalculated/fullBruteTime*100,2) ) + " % brut" )
    cout("Ratio net = " + str(round(fullNet/fullBruteTime*100,2) ) + " % brut = " + str(round(fullNet/fullCalculated*100,2) ) + " % calculated")

def formatMinutes(TimeInminutes):
    
    days    = divmod(TimeInminutes, 60*24)
    hours   = divmod(days[1], 60)
    minutes = divmod(hours[1], 1)


    result = ""
    
    if days[0] != 0 :
        result+= "%d d "%days[0]
    if hours[0] != 0:
        result+= "%d h "%hours[0]
    if minutes[0] != 0 :
        result+= "%d m "%minutes[0]
    if minutes[1]*60 != 0 :
        result+= "%d s "%(minutes[1]*60)

    return result 


def launch(progressBar, logLabel, filterDataList , app ) :
    
    f = open('c:/temp/coucou.html', 'w')
    f.write("<!DOCTYPE html><html><head><title>Page Title</title></head><body><dir>")


    def cout(text) :
        text = text.replace(" ","&nbsp;")
        text = text.replace("\n","<br>")
        text = text.replace("<font&nbsp;color=","<font color=")
        f.write(str(text)+"<br>\n")
        #textLineList.append(str(text))
        #logLabel.setText("<br>".join(textLineList))



    eventFilter_List=[]
    for filterData in filterDataList :
        eventFilter_List.append( event_filter(*filterData))


    progressBar.setFormat("Querying database")
    textLineList=["<font color='#000000'>Results : </font>"]
    

    sg = app.engine.tank.shotgun
    projectId = app.context.project #  {"type":'Project',"id":186}


    cout("Retrieving project workstation list : " + str(projectId) )


    eventFilterList = ['version_up','save_file_as', 'open_file', 'file_publish', 'new_file','open_file','open_file_snapshot' ]
    filters = [ ["project", "is", projectId],  ["event_type", "in", eventFilterList ]  ]


    wsDictList=[] 
    firstEventLog = None 

    eventLogList =  sg.find("EventLogEntry", filters, [ "meta" , "created_at"] )
    cout("got It ! ")

    for eventLog in eventLogList :
        if eventLog["meta"].has_key("ws") :
            if not eventLog["meta"]["ws"] in wsDictList :
                wsDictList.append(eventLog["meta"]["ws"])
        
            if not firstEventLog : 
                firstEventLog = eventLog
            elif firstEventLog["id"] > eventLog["id"] :
                firstId = eventLog


    textLineList.append("&nbsp; &nbsp; &nbsp;->&nbsp;" +   " + ".join(wsDictList))

    cout("First event " + str(firstEventLog["created_at"]) )


    cout("Retrieving every event list since " + str(firstEventLog["created_at"])   )
    filters = [ ["created_at", "greater_than", firstEventLog["created_at"]] ,
                ["entity", 'is_not', None],
                ["event_type", "in", eventFilterList ]  ]




    wsDict = {}
    eventLogList = sg.find("EventLogEntry", filters, [ "meta", "entity", "project", "event_type", "created_at"  ] )
    cout("got It ! ")
    for eventLog in eventLogList : 
        thisProject = False
        if eventLog['project']['id'] ==  projectId['id'] :
            thisProject = True

       
        dataEvent = sg_Event( eventLog["created_at"],  eventLog["entity"],  eventLog["event_type"],  thisProject, eventLog["id"])
        # event_datetime, event_context, event_type, thisProject = True  

        if not wsDict.has_key(eventLog["meta"]["ws"]) :
            wsDict[eventLog["meta"]["ws"]] = [dataEvent]
        else :
            wsDict[eventLog["meta"]["ws"]].append(dataEvent)

    progressBar.setFormat("Computing events")

    ev = 0
    stepProgressBar = 0 
    progressBar.setValue(stepProgressBar)


    workstationDict = {}
    for workstation,dailyEventQueue in wsDict.iteritems():
        if str("DUAL8WIN08") != str(workstation):
            pass

        contextList = get_contextList(dailyEventQueue)
        array_2D    = makeArray( dailyEventQueue, contextList ) 
        

        cout("&nbsp; &nbsp; &nbsp;->&nbsp;" + str(workstation)  )

        dayContext_timeTree = calculateArray(array_2D, contextList, eventFilter_List, cout)
        drawArray(array_2D, eventFilter_List,  cout)

        workstationDict[workstation]=dayContext_timeTree

        """
        for k,v in dayContext_timeTree.iteritems():
            cout(str(k))
            for l,m in dayContext_timeTree[k].iteritems():
                cout("  "+ str(l) + " : " + str(m))
        """

   
        ev+= len(array_2D)
        
        stepProgressBar+= 100/len(wsDict.keys())
        progressBar.setValue(stepProgressBar)


    displayDataWS(workstationDict, cout )
    displayDataContext(workstationDict, cout )
    progressBar.setValue(100)
    progressBar.setFormat("Computing done")

    cout("done :  " +  str (ev) )
    
    f.write("</dir></body></html>")
    f.close()