import datetime


class sg_Event(object) :
    
    isLast_sc  = None 
    isFirst_sc = None

    def __init__(self, event_datetime, event_context, event_type, thisProject = True  ) :
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
            
            delta = self.when-other.when
            return (delta.seconds + delta.microseconds/1E6)/60.0



class event_filter(object) :

    def __init__(self, timeIn = datetime.time(0,12,30), timeOut = datetime.time(0,14,00) , timeRem=datetime.time(0,45,0) , timeInactivity=datetime.time(1,0,0), context=None ):
        
        self.timeIn  = timeIn
        self.timeOut = timeOut
        self.deltaRem = datetime.timedelta(hours=timeRem.hour, minutes=timeRem.minute, seconds=timeRem.second)

        self.deltaInactivity = datetime.timedelta(hours=timeInactivity.hour, minutes=timeInactivity.minute, seconds=timeInactivity.second)

        self.context = context

    def calculate(self, event, nextEvent):
        # is matching the inactivityTime ?

        # event-nextEvent

        if not (event-nextEvent) < (self.deltaInactivity.seconds/60.0) :
            # this two events do not match the filters inactivity duration
            return 0.0

        if self.context != None :
            if event.context == nextEvent.context :
                if event.context != self.context :
                    return 0.0 

        if self.timeIn <= event.when.time() and nextEvent.when.time()<=selt.timeOut :
            # ces deux evenement sont contenus dans les bornes du filtres
            return ( -1 * (self.deltaRem.seconds/60) )

        elif self.timeIn <= event.when.time() and nextEvent.when.time() > selt.timeOut :
            minutes = durationBetweenTwoTimes(event.when.time(), self.timeOut )
            if minutes >= (self.deltaInactivity.seconds/60.0) :
                return ( -1 * (self.deltaRem.seconds/60) )

        


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


def drawArray(array_2D, command ):
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
                    newA.append("<font color='#555555'>"+ i.type.rjust(3)+"</font>") 
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
            daystr = "<font color='#666666'>"+str("%03d" %event.when.day).ljust(4)+"</font>"

        command(  daystr + "->"+  "".join(newA) + "  " + str(event.when.time()) + "     " + str(getTimeDelta(array_2D, idx))[0:5])
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


        



def calculateArray(array_2D, contextList) :
    
       
    FILTER = [event_filter( ),
              event_filter(timeIn = datetime.time(0,12,30), timeOut = datetime.time(0,14,00) , timeRem=datetime.time(0,45,0) , timeInactivity=datetime.time(1,0,0), context=None ),
             ]


    contextTimeDict = {}
    for  context in contextList :
        contextTimeDict[str(context)] = 0.0

    
    for idx in range(len(array_2D)) :
         
        event , nextEvent_sc = getNextEvent_sameContext(array_2D, idx)
        


        nextEvent = getNextEvent(array_2D, idx)
        if nextEvent :
            
            # le cas AA
            if event.context  ==  nextEvent.context :   
                contextTimeDict[str(event.context)] += event-nextEvent
            
            # le cas AB
            else :
                if not event.isLast_sc :
                    if not nextEvent_sc.type in ["n","o"] :
                        # measured time goes to A
                        contextTimeDict[str(event.context)] += event-nextEvent                       
                    else :
                        # do not add time to A
                        #contextTimeDict[str(event.context)] += 0.0
                        pass
                else :
                    nextEvent , prevEvent_sc = getPrevEvent_sameContext(array_2D, idx+1)
                    if prevEvent_sc :
                        contextTimeDict[str(nextEvent.context)] += event-nextEvent
                    else :
                        #contextTimeDict[str(event.context)] += 0.0
                        pass

        idx += 1



def launch(progressBar, logLabel,  app ) :



    progressBar.setFormat("Querying database")
    textLineList=["<font color='#000000'>Results : </font>"]
    def cout(text) :
        text = text.replace(" ","&nbsp;")
        text = text.replace("\n","<br>")
        text = text.replace("<font&nbsp;color=","<font color=")
        textLineList.append(str(text))
        logLabel.setText("<br>".join(textLineList))

    sg = app.engine.tank.shotgun
    projectId = {"type":'Project',"id":186} # app.context.project)


    cout("Retrieving project workstation list : " + str(projectId) )


    eventFilterList = ['version_up','save_file_as', 'open_file', 'file_publish', 'new_file','open_file','open_file_snapshot' ]
    filters = [ ["project", "is", projectId],  ["event_type", "in", eventFilterList ]  ]


    wsDictList=[] 
    firstEventLog = None 

    for eventLog in  sg.find("EventLogEntry", filters, [ "meta" , "created_at"] )  :
        if eventLog["meta"].has_key("ws") :
            if not eventLog["meta"]["ws"] in wsDictList :
                wsDictList.append(eventLog["meta"]["ws"])
        
            if not firstEventLog : 
                firstEventLog = eventLog
            elif firstEventLog["id"] > eventLog["id"] :
                firstId = eventLog


    textLineList.append("&nbsp; &nbsp; &nbsp;->&nbsp;" +   " + ".join(wsDictList))

    cout("First event" + str(firstEventLog["created_at"]) )


    cout("Retrieving every event list since " + str(firstEventLog["created_at"])   )
    filters = [ ["created_at", "greater_than", firstEventLog["created_at"]] ,
                ["entity", 'is_not', None],
                ["event_type", "in", eventFilterList ]  ]




    wsDict = {}
    for eventLog in sg.find("EventLogEntry", filters, [ "meta", "entity", "project", "event_type", "created_at"  ] ) : 
        thisProject = False
        if eventLog['project']['id'] ==  projectId['id'] :
            thisProject = True

        #dataEvent = {"thisProject" : thisProject, "task" : eventLog["entity"], "created_at" : eventLog["created_at"], "event_type" : eventLog["event_type"] }

        dataEvent = sg_Event( eventLog["created_at"],  eventLog["entity"],  eventLog["event_type"],  thisProject)
        # event_datetime, event_context, event_type, thisProject = True  

        if not wsDict.has_key(eventLog["meta"]["ws"]) :
            wsDict[eventLog["meta"]["ws"]] = [dataEvent]
        else :
            wsDict[eventLog["meta"]["ws"]].append(dataEvent)

    progressBar.setFormat("Computing events")

    ev = 0
    stepProgressBar = 0 
    progressBar.setValue(stepProgressBar)

    for workstation,dailyEventQueue in wsDict.iteritems():

        contextList = get_contextList(dailyEventQueue)
        array_2D    = makeArray( dailyEventQueue, contextList ) 
        

        cout("&nbsp; &nbsp; &nbsp;->&nbsp;" + str(workstation)   )

        calculateArray(array_2D, contextList)
        drawArray(array_2D, cout)
        ev+= len(array_2D)
        
        stepProgressBar+= 100/len(wsDict.keys())
        progressBar.setValue(stepProgressBar)

    cout("done :  " +  str (ev) )