import os
import numpy as np
from .animation import *

def upper_strings(l):
    if l is None:
        return None
    return list(map(lambda x : x.upper(), l))

def import_bvh(path, log=False):
    with open(path, "r") as file:
        if log:
            print("bvh file name:", os.path.split(path)[-1])
        bvh = file.read()

    hierarchy_start = bvh.find("HIERARCHY")
    hierarchy_end = bvh.find("MOTION")

    hierarchy_section = bvh[hierarchy_start:hierarchy_end]
    motion_section = bvh[hierarchy_end:]

    parts = {}
    namestack = []
    roots = []
    names = []
    site_cnt = 0
    joint_cnt = 0
    offset_dist_sum = 0

    for line in hierarchy_section.split('\n'):
        if len(line.strip()) == 0:
            continue
        prefix = line.strip().split()
        args = prefix[1:]
        prefix = prefix[0]

        if prefix in ['ROOT', 'JOINT']:
            parts[args[0]] = {'children': [], 'parent': None}
            namestack.append(args[0])
            if prefix == 'ROOT':
                roots.append(args[0])
            joint_cnt += 1
            names.append(args[0])

        elif prefix == 'End':
            name = f'End Site{site_cnt}'
            parts[name] = {'children': [], 'parent': None}
            namestack.append(name)
            site_cnt += 1

        elif prefix == 'OFFSET':
            offset = glm.vec3(list(map(float, args)))
            parts[namestack[-1]]['offset'] = offset
            offset_dist_sum += glm.l2Norm(offset)

        elif prefix == 'CHANNELS':
            parts[namestack[-1]]['channels'] = args[1:]
            
        elif prefix == '}':
            curname = namestack.pop()
            if(len(namestack) > 0):
                parts[namestack[-1]]['children'].append(curname)
                parts[curname]['parent'] = namestack[-1]
    
    objects = {}

    def construct(partname):
        part = parts[partname]
        parentname = part['parent']
        name = f'{part["parent"]}-{partname}'

        objects[partname] = GLSkeleton(
            name= name,
            parent= objects.get(parentname),
            offset=parts[partname]['offset'],
            channels= upper_strings(part.get('channels')),
            thickness = offset_dist_sum / (len(parts)-len(roots)) / 3,
            enable_mesh= partname not in roots
        )

        for childname in part['children']:
            construct(childname)

    for root in roots:
        construct(root)

    motion_section_splitted = motion_section.split('\n')

    motion = []

    for line in motion_section_splitted[3:]:
        if len(line.strip()) == 0:
            continue
        motion.append(list(map(float, line.strip().split())))

    object_keys = list(objects.keys())
    object_values = list(objects.values())
    frames = int(motion_section_splitted[1].split(':')[-1])
    framerate = float(motion_section_splitted[2].split(':')[-1])

    if log:
        print("Number of frames:", frames)
        print("fps:", round(1 / framerate, 2))
        print("Number of joints:", joint_cnt)
        print("List of all joint names:", names)

    return GLAnimationInterpolated(
        skeletons= object_values,
        roots= [object_keys.index(element) for element in roots],
        motion= np.array(motion),
        frames= frames,
        framerate= framerate
    )
