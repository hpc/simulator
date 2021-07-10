def getStrings():
    grizzly_workload = """
    
    grizzly-workload:{ 
        option:value,
        option:value,
        ...
    }
    
    Required:

        "time": "STR"                               Where STR is the amount of time to include in the
                                                    workload.  The format of this quoted string is:
                                                    :                                   all data
                                                    Month-Day-Year:                     from this date until end
                                                    :Month-Day-Year                     from start until this date
                                                    Month-Day-Year : Month-Day-Year     from this date to this date
        
        "input": "PATH"                             Where PATH is location of jobs csv file (sanitized or not)

    Optional:
        "number-of-jobs": INT                       The number of jobs wanted from the start.If negative,
                                                    it is the amount
                                                    of jobs from the end going backward.If not specified,
                                                    all jobs in the time range are included.
                                                    required for --random-selection

        "scale-widths-based-on": INT                change the widths of jobs based on:
                                                    'new_width = old_width * --nodes/INT'
                                                    where old_width is what the input is based on
                                                    Since grizzly data is based on 1490 nodes
                                                    this is typically the value for INT
         
              
        "random-selection":true|false               To get a random selection of jobs

        "submission-time": <FLOAT><:exp|fixed>      This dictates the time between submissions and what kind of randomness.
                           <FLOAT:FLOAT:unif>       If zero is used for a float,combined with ":fixed" then all jobs will start at time zero.
                                                    If omitted, grizzly data will be used.
                                                            
                                                    exp: This will be exponentially distributed, random values with mean time between submissions to be FLOAT.
                                                    fixed: All jobs will have this time between them unless zero is used for a FLOAT.
                                                    unif: This will be uniform, random values from min:max
                                                    ex:     
                                                            "submission-time": "200.0:exp"
                                                            "submission-time": "100.0:fixed"
                                                            "submission-time": "0.0:fixed"
                                                            "submission-time": "0:200.0:unif"

        "wallclock-limit":<FLOAT|INT%|STR>          wallclock limits will all be set to this for FLOAT. (-1) means the value will not be used in Batsim.
                                                    wallclock limits will be a % of run time for INT%
                                                    wallclock limits will be random from min % of runtime to max % in STR format '"min%:max%"'
                                                    wallclock limits will be random seconds from min to max in STR format  '"min:max"'
                                                    wallclock limits will be what the grizzly data is if not set.
                                                    ex:     "wallclock-limit": -1
                                                            "wallclock-limit": 500.3
                                                            "wallclock-limit": "101%"
                                                            "wallclock-limit": "50%:150%"
                                                            "wallclock-limit": "100:3000"
        "read-time": <FLOAT|INT%|"STR">             set this fixed time to readtime in seconds for FLOAT.
                                                    set this to % of run time for INT%.
                                                    set this to random % of run time for STR format "min%:max%"
                                                    set this to random seconds from min to max in STR format   "min:max".
                                                    readtime will be omitted in the workload if not included.
                                                    ex:     "read-time": 20
                                                            "read-time": "2%"
                                                            "read-time": "2%:4%"
                                                            "read-time": "2:20"

        "dump-time": <FLOAT|INT%|"STR">             set this fixed time to dumptime in seconds for FLOAT.
                                                    set this to % of run time for INT%.
                                                    set this to random % of run time for STR format "min%:max%"
                                                    set this to random seconds from min to max in STR format   "min:max".
                                                    dumptime will be omitted in the workload if not included.
                                                    ex:     "dump-time": 20
                                                            "dump-time": "3%"
                                                            "dump-time": "3%:5%"
                                                            "dump-time": "3:30"

        "checkpoint-interval": <FLOAT|INT%|"STR">   set this fixed time to checkpoint in seconds for FLOAT.
                                                    set this to % of run time for INT%.
                                                    set this to random % of run time for STR format "min%:max%"
                                                    set this to random seconds from min to max in STR format   "min:max".
                                                    checkpoint will be omitted in the workload if not included.
                                                    ex:     "checkpoint-interval": 120
                                                            "checkpoint-interval": "30%"
                                                            "checkpoint-interval": "10%:30%"
                                                            "checkpoint-interval": "120:240"
    

    """
    synthetic_workload="""
        "synthetic-workload":{
            "option":value,
            "option":value,
            ...
        }

Required Options:
    number-of-jobs: <INT>                           total number of jobs in this workload
      
    number-of-resources:  <INT:fixed>               This dictates the number of resources used for each job and the kind of randomness.
                          <INT:INT:unif>            INT must be > 0
                          <FLOAT:FLOAT:norm>
                          <STR:pos:csv>      
                                                    fixed: All jobs will have INT for number of resources.
                                                    csv: Will come from file at STR.  pos is the position in each row that holds resources. 0 is first column.
                                                    unif: This will be uniform, random values from min:max
                                                    norm: normal distribution, random values with FLOAT:FLOAT = mu:sigma = mean:std_deviation
                                                    variations of min:max include:
                                                            :		    1 to the total amount of resources
                                                            min:		min to the total amount of resources
                                                            :max		1 to max
                                                            min:max		min to max
                                                    ex:     
                                                            'number-of-resources: "50:fixed"'
                                                            'number-of-resources: "::unif"'
                                                            'number-of-resources: "2::unif"'
                                                            'number-of-resources: ":10:unif"'
                                                            'number-of-resources: "2:10:unif"'
                                                            'number-of-resources: "~/500000.csv:0:csv"'

    
    duration-time:  <FLOAT><:exp|fixed>             This dictates the duration times and what kind of randomness. FLOAT must be > 0.
                    <FLOAT:FLOAT:unif>
                    <FLOAT:FLOAT:norm>      
                    <STR:pos:time:csv>              exp: This will be exponentially distributed, random values with mean time of durations to be FLOAT.
                                                    fixed: All jobs will have FLOAT for a duration.
                                                    csv: Will come from file at STR.  pos is the position in each row that holds resources. 0 is first column. h|m|s for time.hour|minute|second
                                                    unif: This will be uniform, random values from min:max
                                                    norm: normal distribution, random values with FLOAT:FLOAT = mu:sigma = mean:std_deviation
                                                    variations of min:max include:
                                                            :		    1 to the total amount of resources
                                                            min:		min to the total amount of resources
                                                            :max		1 to max
                                                            min:max		min to max
                                                    ex:     
                                                            'duration-time: "200.0:exp"'
                                                            'duration-time: "100.0:fixed"
                                                            'duration-time: "0:200.0:unif"'
                                                            'duration-time: "~/500000.csv:1:h:csv"'
                
    submission-time:  <FLOAT><:exp|fixed>           This dictates the time between submissions and what kind of randomness.
                      <FLOAT:FLOAT:unif>            If zero is used for a float,combined with ":fixed" then all jobs will start at time zero.
                      <FLOAT:FLOAT:norm>
                                                            
                                                    exp: This will be exponentially distributed, random values with mean time between submissions to be FLOAT.
                                                    fixed: All jobs will have this time between them unless zero is used for a FLOAT.
                                                    unif: This will be uniform, random values from min:max
                                                    norm: normal distribution, random values with FLOAT:FLOAT = mu:sigma = mean:std_deviation
                                                    variations of min:max include:
                                                            :		    1 to the total amount of resources
                                                            min:		min to the total amount of resources
                                                            :max		1 to max
                                                            min:max		min to max
                                                    ex:     
                                                            'submission-time: "200.0:exp"'
                                                            'submission-time: "100.0:fixed"'
                                                            'submission-time: "0.0:fixed"'
                                                            'submission-time: "0:200.0:unif"'
Optional Options:
                                                                                            
    wallclock-limit: <FLOAT|INT%|STR>               wallclock limits will all be set to this for FLOAT. (-1) means the value will not be used in Batsim.
                                                    wallclock limits will be a % of run time for INT%
                                                    wallclock limits will be random(discrete unif) from min % of runtime to max % in STR format '"min%:max%"'
                                                    wallclock limits will be random(discrete unif) seconds from min to max in STR format  '"min:max"'
                                                    wallclock limits will be -1 if not set
                                                    ex:     'wallclock-limit: -1'
                                                            'wallclock-limit: 500.3'
                                                            'wallclock-limit: "101%"'
                                                            'wallclock-limit: "50%:150%"'
                                                            'wallclock-limit: "100:3000"'

    read-time: <FLOAT|INT%|STR>                     set this fixed time to readtime in seconds for FLOAT.
                                                    set this to % of run time for INT%.
                                                    set this to random(discrete unif) % of run time for STR format "min%:max%"
                                                    set this to random(discrete unif) seconds from min to max in STR format   "min:max".
                                                    readtime will be omitted in the workload if not included.
                                                    ex:     'read-time: 20'
                                                            'read-time: "2%"'
                                                            'read-time: "2%:4%"'
                                                            'read-time: "2:20"'

    dump-time: <FLOAT|INT%|STR>                     set this fixed time to dumptime in seconds for FLOAT.
                                                    set this to % of run time for INT%.
                                                    set this to random(discrete unif) % of run time for STR format "min%:max%"
                                                    set this to random(discrete unif) seconds from min to max in STR format   "min:max".
                                                    dumptime will be omitted in the workload if not included.
                                                    ex:     'dump-time: 20'
                                                            'dump-time: "3%"'
                                                            'dump-time: "3%:5%"'
                                                            'dump-time: "3:30"'

    checkpoint-interval: <FLOAT|INT%|STR>           set this fixed time to checkpoint in seconds for FLOAT.
                                                    set this to % of run time for INT%.
                                                    set this to random(discrete unif) % of run time for STR format "min%:max%"
                                                    set this to random(discrete unif) seconds from min to max in STR format   "min:max".
                                                    checkpoint will be omitted in the workload if not included.
                                                    ex:     'checkpoint-interval: 120'
                                                            'checkpoint-interval: "30%"'
                                                            'checkpoint-interval: "10%:30%"'
                                                            'checkpoint-interval: "120:240"'

    """

    output="""
        "output":{
            option:value,
            option:value,
            ...
        }
        
        
        Options:

        "AAE":true                                  whether you want the average application efficiency computed

        "makespan":true|false                       whether you want the makespan computed in output
                                                    not to be used in conjunction with avg-makespan

        "avg-makespan":INT                          whether you want an average makespan.  If so, how
                                                    many times do you want each experiment to Run to make
                                                    an average of?  Enter that in INT
                                                    
        "pass-fail": LIST                           Test a system for passing a memory test or failing
                                                    The List is composed as follows:
                                                        
                                                        [Trials,Theta,Baseline NMTBF,Allowed Failures]
                                                    
                                                    Trials aka Runs
                                                    Theta is a computed value that is multiplied
                                                        by Baseline NMTBF to get the duration the test must run for
                                                    Baseline NMTBF - say we are testing if it is 2x worse memory.  Baseline refers to 2x worse than what?
                                                    Allowed Failures: pass would be if there were "Allowed Failures" number of failures before the duration
                                                        fail would be if there were "Allowed Failures + 1" or more number of failures before the duration
                                                        
                                                    **** Not to be used with avg-makespan.  Also, this option automatically sets logging verbosity to "information"
                                                    
                                                    

        "raw":INT                                   whether to output raw post processing data
                                                    raw = 1,debug=2, raw and debug=3


    """
    node_sweep="""
    The node sweep should come first since many other sweeps and options are based off of it.
    Start with:
    
        input{
                "node-sweep":{
            
                }
                
                ...
            
            
    Like other sweeps that involve numbers you can use a min, max (inclusive), step:
    Negative steps are acceptable, just make sure it doesn't bring your number to negative or 0.
    Only integers make sense for this sweep.
                
                "node-sweep":{
                    "min":1,
                    "max":5,
                    "step":1
                }
                    
    You can also use a predefined range:
    
                "node-sweep":{
                    "range":[1,4,5]
                }
                
    You can also base it on a formula where the variable "i" is replaced with either
    a min,max,step   or a range:
    
                "node-sweep":{
                    "formula":"(1/2) * i",
                    "min":"2",
                    "max":10,
                    "step":2
                }
                
    or        
                "node-sweep":{
                    "formula":"(1/2) * i",
                    "range":[2,4,6,8,10]
                }
                
    both of these will multiply "i" by (1/2), so for both you would end up with 1,2,3,4,5
    You can use any valid python function including sqrt() for square root and "**" for exponent.
    You can only use "i" as a variable, but you can use it multiple times.

    """
    smtbf_sweep="""
    The SMTBF sweep usually comes after the node-sweep. It is the "System Mean Time Between Failure" for the whole cluster.
    The value is in seconds.
    
    You can specify, instead, the "Node Mean Time Between Failure" for a single node using the "compute-SMTBF-from-NMTBF" option
    and setting it to true.  This is an example of why you should always use a node-sweep before anything else as this option requires knowing
    the number of nodes of each job.
    
    Note: this will be deterministic when the failures will happen.  If this is the case, an avg-makespan makes no sense as each
        simulation will have the same makespan.  To make the failures random (exponentially distributed random failures where
        a node is uniformally randomly chosen to fail at these exponentially random times), then you must chooose to seed these random numbers with the
        current time.  Use the option "seed-failures":true  in order to achieve this.
    
    Start with:
    
        input{
                "node-sweep":{
                    ...
                },
                
                "SMTBF-sweep":{
                
                }
                
                ...
            
            
    Like other sweeps that involve numbers you can use a min, max (inclusive), step:
    Negative steps are acceptable, just make sure it doesn't bring your number to negative or 0.
                
                "SMTBF-sweep":{
                    "min":200000,
                    "max":400000,
                    "step":50000
                }
                    
    You can also use a predefined range:
    
                "SMTBF-sweep":{
                    "range":[200000,250000,300000,350000,400000]
                }
                
    You can also base it on a formula where the variable "i" is replaced with either
    a min,max,step   or a range:
    
                "SMTBF-sweep":{
                    "formula":"400000 * (1/(2**i))",
                    "min":"1",
                    "max":5,
                    "step":1
                }
                
    or        
                "SMTBF-sweep":{
                    "formula":"400000 * (1/i)",
                    "range":[2,4,8,16,32]
                }
                
    both of these will test for 2x,4x,8x,16x,32x worse failure rates than the 400,000 second baseline.
    Notice the formula for the min,max,step uses 2**i where "**" is the exponential function.  You can use any valid
    python function including sqrt() for square root.  You can only use "i" as a variable, but you can use it multiple times.
    
    
    Example with the NMTBF option and the seed failures option after it:
                "SMTBF-sweep":{
                    "compute-SMTBF-from-NMTBF":true,
                    "formula":"(400*1000) * (1/i)",
                    "range":[2,4,8,16,32]
                },
                "seed-failures":true,

    """

    
    checkpoint_sweep="""
    The checkpoint sweep is a sweep on how often to checkpoint.  This checkpoint interval is in seconds.
    
    This is a number sweep so "min,max,step" works as well as "range" and "formula".
    Negative steps are acceptable, just make sure it doesn't bring your number to negative or 0.
    
    When using "range" you can also set one of the values to "optimal" which will compute the optimal checkpointing for each job.
    Note that you cannot use "formula" if your "range" has "optimal" in it.
    Also, you should include an additional option to your "input" to turn checkpointing on:  "checkpointing-on":true
    
    Start with:
    
        input{
                "node-sweep":{
                    ...
                },
                
                ...
                
                "checkpoint-sweep":{
                    ...
                },
                "checkpointing-on":true,
                
                ...
            
            
    Like other sweeps that involve numbers you can use a min, max (inclusive), step:
                
                "checkpoint-sweep":{
                    "min":3600,
                    "max":,18000,
                    "step":3600
                }
                    
    You can also use a predefined range:
    
                "checkpoint-sweep":{
                    "range":[3600,7200,10800,14400,18000]
                }
                
    You can also base it on a formula where the variable "i" is replaced with either
    a min,max,step   or a range:
    
                "checkpoint-sweep":{
                    "formula":"60*60*i",
                    "min":"1",
                    "max":5,
                    "step":1
                }
                
    or        
                "checkpoint-sweep":{
                    "formula":"(60**2)*i",
                    "range":[1,2,3,4,5]
                }
                
    all of these will do 1,2,3,4,5 hour checkpointing intervals.
    Notice the formula for range uses 60**2 where "**" is the exponential function.  You can use any valid
    python function including sqrt() for square root.  You can only use "i" as a variable, but you can use it multiple times.
    
    
    Example with the "optimal" option:
                "checkpoint-sweep":{
                    "range":[3600,7200,"optimal"]
                }

    """
    checkpoint_error_sweep="""
    The checkpointError sweep is supposed to be used in conjunction with
        
        "checkpoint-sweep":{
            "range":["optimal"]
        },
        checkpointing-on":true,
    
    It is meant for an analysis of what values of Average Application Efficiency you get back
    when going lower than "optimal" or higher than "optimal".  This "error" can be swept through as follows:
    
    This is a number sweep so "min,max,step" works as well as "range" and "formula".
    Negative steps are acceptable, just make sure it doesn't bring your number to negative or 0.
    
        
    
    Start with:
    
        input{
                "node-sweep":{
                    ...
                },
                
                ...
                
                "checkpoint-sweep":{
                    "range":["optimal"]
                },
                checkpointing-on":true,
                "checkpointError-sweep":{
                    
                    ...
                    
                }
                
                ...
            
            
    Like other sweeps that involve numbers you can use a min, max (inclusive), step:
                
                "checkpointError-sweep":{
                    "min":0.1,
                    "max":,4.0,
                    "step":0.1
                }
                    
    You can also use a predefined range:
    
                "checkpointError-sweep":{
                    "range":[0.1,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0]
                }
                
    You can also base it on a formula where the variable "i" is replaced with either
    a min,max,step   or a range:
    
                "checkpointError-sweep":{
                    "formula":"0.1*i",
                    "min":"1",
                    "max":40,
                    "step":1
                }
                
    or        
                "checkpointError-sweep":{
                    "formula":"(10**(-1))*i",
                    "range":[1,5,10,15,20,25,30,35,40]
                }
                
    Notice the formula for range uses 10**(-1) where "**" is the exponential function.  You can use any valid
    python function including sqrt() for square root.  You can only use "i" as a variable, but you can use it multiple times.
    

    """
    performance_sweep="""
    The performance sweep sets the performance of the system.  It is a float based on 1.0 being normal performance.Higher
    than that is a SLOWER system and lower than that is a FASTER system.  
    1.2 would be 20% slower
    0.7 would be 30% faster
    This is a number sweep so "min,max,step" works as well as "range" and "formula".
    Negative steps are acceptable, just make sure it doesn't bring your number to negative or 0.
    
    Start with:
    
        input{
                "node-sweep":{
                    ...
                },
                
                ...
                
                "performance-sweep":{
                    ...
                }
            
            
    Like other sweeps that involve numbers you can use a min, max (inclusive), step:
                
                "performance-sweep":{
                    "min":1.0,
                    "max":0.5,
                    "step":-0.1
                }
                    
    You can also use a predefined range:
    
                "performance-sweep":{
                    "range":[1.0,0.9,0.8,0.7,0.6,0.5]
                }
                
    You can also base it on a formula where the variable "i" is replaced with either
    a min,max,step   or a range:
    
                "performance-sweep":{
                    "formula":"1.0-(0.1*i)",
                    "min":"0",
                    "max":5,
                    "step":1
                }
                
    or        
                "checkpoint-sweep":{
                    "formula":"1.0-((10**(-1))*i)",
                    "range":[0,1,2,3,4,5]
                }
                
    all of these will do 0%,10%,20%,30%,40%,and 50% faster simulations.
    Notice the formula for range uses 10**(-1) where "**" is the exponential function.  You can use any valid
    python function including sqrt() for square root.  You can only use "i" as a variable, but you can use it multiple times.
    

    """
    general="""
    The general format of a config file:
    
    {       <------------------------------------   Opening curly brace to be proper json
    
        "Name1":{       <------------------------   The name of an experiment comes first.  You can have multiple experiments
                                                    in one config file and each will end up in it's own folder under the --output folder.
                                                    Notice the opening and closing curly brace.  Make sure you put a comma after the closing
                                                    curly brace if you plan on having another experiment in the same config file
                
                "input":{    <-------------------   Always make sure you have an input and an output in your experiment
                
                    "node-sweep":{  <------------   It is MOST advisable to always start with a node-sweep.  All other sweeps can come after this one
                    
                    },
                    "synthetic-workload":{ <-----   Always include either a synthetic-workload or a grizzly-workload after your sweeps
                    
                    },
                    "option":value,        <-----   Include any options that will affect all of the jobs on the outside of any sweep or workload
                
                },    <--------------------------   Make sure you separate your input options with commas, but also remember to separate input
                                                    and output with a comma
                "output":{   <-------------------   Again, always make sure you have an input and output in your experiment
                
                    "option":value,   <----------   Output is a bit simpler than input.  Just make sure it is valid json
                    "option":value
                
                }
        
        
        },     <---------------------------------   This closes the experiment and here we have a comma because we included another experiment "Name2"
        "Name2":{
            "input":{
            
                ...  <--------------------------    Make sure you replace this ellipsis with at least:
                                                        * a node-sweep
                                                        * a workload
            },
            "output":{
            
                ...  <--------------------------    You should replace ellipsis with at least:
                                                        * "AAE":true | "makespan":true
                
            }    <------------------------------    Close output
        }  <------------------------------------    Close "Name2"          
    }  <----------------------------------------    Close json
    
    """
    sweeps="""
    Sweeps are what we call it when we need to "sweep" over a set of parameters.  For instance, we want to see what happens when we
    increase the node size of our cluster from 1,000 nodes to 2,000 nodes stepping every 100 nodes.
    
    Sweeps come in the "input" section of our config file and follows the naming convention: NAME-sweep
    You can make your own sweep module as well.  Refer to documentation.
    
    You want to start with a node-sweep as other sweeps rely on this number already being set.
    
    Sweeps work like for-loops in programming.  
    So if we start with a node-sweep...say: 1 nodes to 6 nodes with a step of 1
    we will have experiment_1 as having 1 node, experiment_2 as having 2 nodes, _3 as having 3 nodes,
                 experiment_4 4 nodes, _5 5 nodes, _6 as having 6 nodes
    
    
    If we include a checkpoint-sweep after it...say: 1 hr, 2hr, and 3hr
    we will have experiment_1  - experiment_6  as having a checkpoint interval of 1hr and # nodes 1-6 (experiment_1 = 1 , ... , experiment_6 =6)nodes
    we will have experiment_7  - experiment_12 as having a checkpoint interval of 2hr and # nodes 1-6 (experiment_7 = 1 , ... , experiment_12=6)nodes
    we will have experiment_13 - experiemnt_18 as having a checkpoint interval of 3hr and # nodes 1-6 (experiment_13= 1 , ... , experiment_18=6)nodes
    
    
    
    If we include another sweep...say performance-sweep: 1.0,0.7
    we will have experiment_1  - experiment_6  as having a performance of 1.0, checkpoint interval of 1hr and # nodes 1-6
    we will have experiment_7  - experiment_12 as having a performance of 1.0, checkpoint interval of 2hr and # nodes 1-6
    we will have experiment_13 - experiemnt_18 as having a performance of 1.0, checkpoint interval of 3hr and # nodes 1-6
    
    we will have experiment_19 - experiment_24 as having a performance of 0.7, checkpoint interval of 1hr and # nodes 1-6
    we will have experiment_25 - experiment_30 as having a performance of 0.7, checkpoint interval of 2hr and # nodes 1-6
    we will have experiment_31 - experiemnt_36 as having a performance of 0.7, checkpoint interval of 3hr and # nodes 1-6

    Hopefully this makes sense to you.  Basically, every new sweep will take what was already there for experiments and add it's first
    parameter to these experiments that were already there.  Then it will take what was already there but make them into new experiments and add the 2nd parameter,
    Then it will take what was already there but make them into another new set of experiments and add the 3rd parameter.
    
    Notice we started with a node-sweep and ended up with 6 experiments, then we had 3 parameters on the checkpoint-sweep and we ended up with 18 experiments:6*3
    Then we had a performance-sweep with 2 parameters and we ended up with 36 experiments: 6*3*2
    
    
    
    """
    input_options="""
    
    "checkpointing-on":true                                                     Turn checkpointing on.  This is needed when doing a checkpointing sweep
    
    
    
    seed-failures":true                                                         Seed the random generators for failures with current time to give random results
                                                                                If you omit this, you will have the same results each time.
                                                                                
    
    batsim-log": "information" | "network-only" | "debug" | "quiet"             The level of logging to be done in batsim and output to the file:
                                                                                    ......./--output/experiment_name/experiment_#/Run_#/output/expe-out/log/batsim.log
                                                                                Default is "quiet"
    
    
    
    batsched-log": "info" | "silent" | "debug" | "quiet"                        The level of logging to be done in batsched and output to the file:
                                                                                    ......./--output/experiment_name/experiment_#/Run_#/output/expe-out/log/sched.err.log
                                                                                Default is "quiet"

    """
 
    return {"grizzly-workload":grizzly_workload,"synthetic-workload":synthetic_workload,
        "output":output,
        "node-sweep":node_sweep,"SMTBF-sweep":smtbf_sweep,"checkpoint-sweep":checkpoint_sweep,"checkpointError-sweep":checkpoint_error_sweep,"performance-sweep":performance_sweep,
        "general":general,"sweeps":sweeps,"input-options":input_options}

