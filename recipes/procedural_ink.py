"""Import-inert object-space ink coupon; extracted from fidelity banner experiment.
No camera/light/world edits, no save/render, no production selection. Candidate only.
"""
import math


def apply(obj, period_m=.000625, axes=('X', 'Z'), strength=.65, slot=0):
    import bpy
    if not math.isfinite(period_m) or period_m <= 0:
        raise ValueError('period_m must be positive')
    if not 0 <= strength <= 1 or len(axes) != 2 or any(a not in ('X','Y','Z') for a in axes):
        raise ValueError('invalid strength or axes')
    if obj.type != 'MESH' or not 0 <= slot < len(obj.data.materials):
        raise ValueError('mesh material slot required')
    source = obj.data.materials[slot]
    if source is None or not source.use_nodes:
        raise ValueError('node material required')
    if any(abs(s-1) > 1e-6 for s in obj.scale):
        raise ValueError('metric object-space recipe requires unit object scale; do not silently apply transforms')
    owned = source.get('meta_ink_owner') == obj.name
    if owned and tuple(source['meta_ink_axes']) != tuple(axes):
        raise ValueError('axis change requires a fresh source material')
    material = source if owned else source.copy()
    if not owned:
        material.name = source.name+' · meta ink · '+obj.name
        material['meta_ink_owner'] = obj.name
        material['meta_ink_axes'] = list(axes)
        obj.data.materials[slot] = material
        nt = material.node_tree
        bsdf = next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'), None)
        if bsdf is None:
            obj.data.materials[slot] = source
            bpy.data.materials.remove(material)
            raise ValueError('Principled BSDF required')
        base = bsdf.inputs['Base Color']
        base_socket = base.links[0].from_socket if base.is_linked else None
        base_color = tuple(base.default_value)
        co = nt.nodes.new('ShaderNodeTexCoord')
        split = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(co.outputs['Object'], split.inputs[0])
        def math_node(op, a, b=None, name=None):
            n = nt.nodes.new('ShaderNodeMath')
            n.operation = op
            if name: n.name = name
            for socket, value in zip(n.inputs, (a,b)):
                if value is None: continue
                if isinstance(value,(int,float)): socket.default_value = value
                else: nt.links.new(value, socket)
            return n.outputs[0]
        coords=[]
        for i, axis in enumerate(axes):
            scaled = math_node('MULTIPLY', split.outputs[axis], 1/period_m, 'ML scale '+str(i))
            fract = math_node('FRACT', scaled)
            centered = math_node('SUBTRACT', fract, .5)
            coords.append(math_node('MULTIPLY', centered, centered))
        radius = math_node('ADD', *coords)
        dots = math_node('LESS_THAN', radius, .065)
        amount = math_node('MULTIPLY', dots, strength, 'ML ink strength')
        mix = nt.nodes.new('ShaderNodeMixRGB')
        mix.name = 'ML ink composite'
        mix.blend_type = 'MULTIPLY'
        nt.links.new(amount, mix.inputs[0])
        if base_socket: nt.links.new(base_socket,mix.inputs[1])
        else: mix.inputs[1].default_value = base_color
        mix.inputs[2].default_value = (.12,.17,.22,1)
        nt.links.new(mix.outputs[0],base)
    for i in range(2):
        material.node_tree.nodes['ML scale '+str(i)].inputs[1].default_value = 1/period_m
    material.node_tree.nodes['ML ink strength'].inputs[1].default_value = strength
    return dict(recipe='procedural-ink-v1', receiver=obj.name, material=material.name,
                period_m=period_m, axes=list(axes), strength=strength,
                status='candidate', limitations=['uniform periodic marks are not finished comic art',
                'unit object scale required', 'sampling/render pitch must be measured separately'])
