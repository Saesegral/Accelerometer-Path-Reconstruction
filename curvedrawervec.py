import bpy, csv, mathutils

from mathutils import Vector


def makePathEdges(points):
    edges=[]  
    for i in range(len(points)-1):
        edges.append([i,i+1])
    return edges

def integrate(times, vecs):
    res=[Vector((0.0,0.0,0.0))]
    for i in range(len(times)-1):
        res.append(res[-1]+(vecs[i+1]+vecs[i])/2*(times[i+1]-times[i]))
    return res

def center(vecs):
    avg = Vector((0.0,0.0,0.0))
    for v in vecs:
        avg+=v
    avg/=len(vecs)
    return [v-avg for v in vecs]

#Makes x-axis into sections of possible vector magnitudes and y-axis into number of vectors in that range
def makeMagnitudeGraph(vectors, sections):
    mags=sorted([v.magnitude for v in vectors])
    #shifts it to origin
    mags=[m-mags[0] for m in mags]
    populations=[0]*sections
    count=1
    for l in range(len(mags)):
        while mags[l] > mags[-1]*count/sections:
            count+=1
        populations[count-1]+=1
    popVecs = []
    for i in range(len(populations)):
        popVecs.append(Vector((i,0,populations[i])))
    return popVecs
     
#Helpful function, not necessary
def makeNoiseCurves(sections = 30):
    makeCurve("Populations4", makeMagnitudeGraph(getAccelData(fp("still4"))[1],sections))
    makeCurve("Populations10", makeMagnitudeGraph(getAccelData(fp("still10"))[1],sections))
    makeCurve("Populations20", makeMagnitudeGraph(getAccelData(fp("still20"))[1],sections))
    makeCurve("Populations40", makeMagnitudeGraph(getAccelData(fp("still40"))[1],sections))


def getAccelData(name, threshold=7):
    #only collects data after the threshold, the first 7 points or so is off for the fastest polling data, other rates don't seem to be affected.
    
    #Need to fix the file path so that it's not dependent to my computer
    fp = "C:/Users/Clear/Documents/GitHub/Accelerometer-Path-Reconstruction/Paths/" + name +".tsv"
    with open(fp) as tsvfile:
        rdr = csv.reader(tsvfile, delimiter='\t')
        times=[]
        accels=[]
        for i, row in enumerate( rdr ):
            if i <= threshold: continue
            times.append(float(row[1]))
            accels.append(Vector([float(n) for n in row[2:5]]))
    return times, accels

#Not the best way to do this
def cleanData(times, accelVecs, pollingSpeed, errorBuffer):
    #noise is the max magnitude of a deviation of polling data from the resting position
    noise = [0.022574040929888257, 0.05322117164984478, 0.03873575658953424, 0.05056262696616997]
    accelVecs = center(accelVecs)
    cleanTimes=[]
    cleanVecs=[]
    for i in range(len(accelVecs)):
        #screens out data that is below the noise barrier
        if accelVecs[i].magnitude >= noise[pollingSpeed]+errorBuffer:
            cleanTimes.append(times[i])
            cleanVecs.append(accelVecs[i])
    return cleanTimes, cleanVecs

def makeCurves(curveName, times, accelVecs):
    velVecs = integrate(times, accelVecs)
    posVecs = integrate(times, velVecs)
    makeCurve("Acceleration "+curveName, accelVecs)
    makeCurve("Velocity "+curveName, velVecs)
    makeCurve("Position "+curveName, posVecs)
   
def makeCurve(curveName, points):
    profile_mesh = bpy.data.meshes.new(curveName)
    profile_mesh.from_pydata(points, makePathEdges(points), [])
    profile_mesh.update()
    profile_object = bpy.data.objects.new(curveName, profile_mesh)
    profile_object.data = profile_mesh  # this line is redundant .. it simply overwrites .data
    scene = bpy.context.collection
    scene.objects.link(profile_object)
    

#The suffix 04, 10, 20, and 40 represent the approximate Hz of the polling data.

#name = "figure8"
#name = "walkingaround"
#name = "chair"
#name = "toss"
#name = "nothing"
#name = "circle10"
#name = "arc04"
#name = "singlecircle"
#name = "knot10"
#name = "fastcircle10"
still = ["still4","still10","still20","still40"]

name = "fastcircle10"

#This doesn't work because I haven't subtracted the average out.
times, accelVecs = getAccelData(name)
print("Before Clean: times = {}, accels = {}".format(len(times), len(accelVecs)))
times, accelVecs = cleanData(times, accelVecs, 1, 4)
print("After Clean:  times = {}, accels = {}".format(len(times), len(accelVecs)))

makeCurves(name, times, accelVecs)


'''
noises=[]
for i in range(4):
    noises.append(maxNoise(i))
print(noises)
'''

'''
maxNoise(0) == 0.022574040929888257
maxNoise(1) == 0.05322117164984478
maxNoise(2) == 0.03873575658953424
maxNoise(3) == 0.05056262696616997

maxNoise = [0.022574040929888257, 0.05322117164984478, 0.03873575658953424, 0.05056262696616997]
'''

'''
Avg Noise
still4  avgNoise(0) == 0.008377391523107588
still10 avgNoise(1) == 0.017710156762433756
still20 avgNoise(2) == 0.017045449123554986
still40 avgNoise(3) == 0.014517065775709923

avgNoise = [0.008377391523107588, 0.017710156762433756, 0.017045449123554986,0.014517065775709923]
'''

#Get the average delta time for each polling frequency as well.

'''
def avgNoise(pollingSpeed):
    #file names of the still capture data for approximately 30 seconds each
    still = ["still4","still10","still20","still40"]
    fp = "C:/Users/Clear/Documents/GitHub/Accelerometer-Path-Reconstruction/Paths/" + still[pollingSpeed] +".tsv"
    threshold = 7
    with open(fp) as tsvfile:
        rdr = csv.reader(tsvfile, delimiter='\t')
        accels=[]
        for i, row in enumerate( rdr ):
            if i <= threshold: continue
            accels.append(Vector([float(n) for n in row[2:5]]))
    accels = center(accels)
    avg = 0
    for v in accels:
        avg+=v.magnitude
    avg/=len(accels)
    return avg

def maxNoise(pollingSpeed):
    #file names of the still capture data for approximately 30 seconds each
    still = ["still4","still10","still20","still40"]
    fp = "C:/Users/Clear/Documents/GitHub/Accelerometer-Path-Reconstruction/Paths/" + still[pollingSpeed] +".tsv"
    threshold = 7
    with open(fp) as tsvfile:
        rdr = csv.reader(tsvfile, delimiter='\t')
        accels=[]
        for i, row in enumerate( rdr ):
            if i <= threshold: continue
            accels.append(Vector([float(n) for n in row[2:5]]))
    accels = center(accels)
    max = 0
    for v in accels:
        if v.magnitude>max:
            max=v.magnitude
    return max
'''