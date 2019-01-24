import bpy, csv, mathutils

from mathutils import Vector

def getAccelData(fp, threshold=10):
    #only collects data after the threshold, they tend to be off

    with open(fp) as tsvfile:
        rdr = csv.reader(tsvfile, delimiter='\t')
        ts=[]
        accels=[]
        for i, row in enumerate( rdr ):
            if i <= threshold: continue
            ts.append(float(row[1]))
            accels.append(Vector([float(n) for n in row[2:5]]))
    return accels,ts

def makePathEdges(points):
    edges=[]  
    for i in range(len(points)-1):
        edges.append([i,i+1])
    return edges

def integrate(vecs, times):
    res=[Vector((0.0,0.0,0.0))]
    for i in range(len(times)-1):
        res.append(res[-1]+(vecs[i+1]+vecs[i])/2*(times[i+1]-times[i]))
    return res
    
def makeCurve(curveName, points):
    profile_mesh = bpy.data.meshes.new(curveName)
    profile_mesh.from_pydata(points, makePathEdges(points), [])
    profile_mesh.update()
    profile_object = bpy.data.objects.new(curveName, profile_mesh)
    profile_object.data = profile_mesh  # this line is redundant .. it simply overwrites .data
    scene = bpy.context.collection
    scene.objects.link(profile_object)
    
def makeCurves(curveName, accelVecs, times):
    #Subtracts off the first acceleration from all accelerations to counteract gravity.
    #accelVecs = [a-accelVecs[0] for a in accelVecs]
    #Subtracts off the average acceleration from all accelerations to counteract gravity.
    avg = Vector((0.0,0.0,0.0))
    for a in accelVecs:
        avg+=a
    avg/=len(accelVecs)
    accelVecs = [a-avg for a in accelVecs]
    velVecs = integrate(accelVecs, times)
    posVecs = integrate(velVecs, times)
    makeCurve("Acceleration "+curveName, accelVecs)
    makeCurve("Velocity "+curveName, velVecs)
    makeCurve("Position "+curveName, posVecs)



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
name = "fastcircle10"

#Need to fix the file path so that it's not dependent to my computer
fp = "C:/Users/Clear/Documents/GitHub/Accelerometer-Path-Reconstruction/Paths/" + name +".tsv"

accelVecs, ts = getAccelData(fp)

makeCurves(name, accelVecs, ts)