import bpy, csv, math, numpy


#name = "figure8"
#name = "walkingaround"
#name = "chair"
#name = "toss"
#name = "nothing"
name = "circle10"


#Need to fix the file path so that it's not dependent to my computer
fp = "C:/Users/Clear/Documents/GitHub/Accelerometer-Path-Reconstruction/Paths/" + name +".tsv"


with open(fp) as tsvfile:
    rdr = csv.reader(tsvfile, delimiter='\t')
    ts=[]
    accels=[]
    for i, row in enumerate( rdr ):
        #remove the first few pieces of data, they tend to be off
        if i <= 5: continue
        ts.append(float(row[1]))
        accels.append([float(n) for n in row[2:5]])





#Subtracts the first entry from all the points
def initialize(points):
  if isinstance(points, float):
    return [p-points[0] for p in points]
  return [tuple(numpy.subtract(p, points[0])) for p in points]
    
def delta(points):
    deltas=[]
    for i in range(len(points)-1):
        deltas.append(points[i+1]-points[i])
    return deltas

def avg(points):
    avgs=[]
    for i in range(len(points)-1):
        avgs.append([p/2 for p in tuple(numpy.add(points[i+1],points[i]))])
    return avgs

def makePathEdges(points):
    edges=[]  
    for i in range(len(points)-1):
        edges.append([i,i+1])
    return edges

def integrate(vecs, times):
    dt=delta(times)
    average=avg(vecs)
    res=[(0.0,0.0,0.0)]
    for i in range(len(times)-1):
        res.append(tuple(numpy.add(res[-1],tuple([v*dt[i] for v in average[i]]))))
    return res



accels = initialize(accels)
accelEdges=makePathEdges(accels)

vels = integrate(accels, ts)
velEdges = makePathEdges(vels)

poss = integrate(vels, ts)
posEdges = makePathEdges(poss)





profile_mesh = bpy.data.meshes.new("Acceleration "+name)
profile_mesh.from_pydata(accels, accelEdges, [])
profile_mesh.update()
profile_object = bpy.data.objects.new("Acceleration "+name, profile_mesh)
profile_object.data = profile_mesh  # this line is redundant .. it simply overwrites .data
scene = bpy.context.collection
scene.objects.link(profile_object)

profile_mesh = bpy.data.meshes.new("Velocity "+name)
profile_mesh.from_pydata(vels, velEdges, [])
profile_mesh.update()
profile_object = bpy.data.objects.new("Velocity "+name, profile_mesh)
profile_object.data = profile_mesh  # this line is redundant .. it simply overwrites .data
scene = bpy.context.collection
scene.objects.link(profile_object)

profile_mesh = bpy.data.meshes.new("Position "+name)
profile_mesh.from_pydata(poss, posEdges, [])
profile_mesh.update()
profile_object = bpy.data.objects.new("Position "+name, profile_mesh)
profile_object.data = profile_mesh  # this line is redundant .. it simply overwrites .data
scene = bpy.context.collection
scene.objects.link(profile_object)