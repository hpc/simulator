#from_array_to_intervalset
#takes an unsorted list of numbers and returns a string representation
# example:
# input: [0,1,5,6,7,10,20,30,31,32]
# output: "0-1 5-7 10 20 30-32"
def from_list_to_intervalset(array):
    array.sort()
    intervalset=""
    #ok array is sorted
    previous_value=0
    for i in range(0,len(array)):
        if i==0:
            intervalset+=str(array[i])
        else:
            if not(intervalset[len(intervalset)-1] == '-'):
                #ok we are not in a current interval
                if array[i] == (previous_value+1):
                    #ok we need to start an interval
                    intervalset+="-"
                    if i==len(array)-1:
                        #ok we need to end the interval, we are at the end
                        intervalset+=str(array[i])
                else:
                    #ok we need to put the number in the intervalset
                    intervalset+=" "+str(array[i])
            else:
                #ok we are in a current interval
                if array[i] == (previous_value+1):
                    #ok the intervalset continues
                    if i==len(array)-1:
                        #ok we are at the end, we need to close off the interval
                        intervalset+=str(array[i])
                    else:
                        #ok we need to continue the interval by doing nothing
                        intervalset+=""
                else:
                    #ok we need to finish the interval
                    intervalset+=str(previous_value)+" "+str(array[i])
        previous_value=array[i]
    return intervalset

def from_intervalset_to_list(string):
    ourList=[]
    strings=string.split(" ")
    for aString in strings:
        aSplit=aString.split("-")
        if len(aSplit)==1:
            #just a single number
            ourList.append(int(aSplit[0]))
        else:
            ourList+=list(range(int(aSplit[0]),int(aSplit[1])+1))

    return ourList
def size_of_intervalset(string):
    return len(from_intervalset_to_list(string))
