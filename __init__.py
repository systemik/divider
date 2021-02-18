# Divider v3
# Licensed under GPLv3

bl_info = {
    "name": "divider",
    "author": "Systemic",
    "version": (0, 0, 1),
    "blender": (2, 90, 0),
    "location": "View3D > Tool Shelf > divider Tab",
    "description": "Create divisions",
    "wiki_url": "https://github.com/systemik/divider",
    "category": "3D View",
    "warning": "Early beta"
}


import bpy, bmesh, random, math, mathutils
from bpy.props import (IntProperty, FloatProperty, BoolProperty, PointerProperty)
from bpy.types import (Panel, Operator, PropertyGroup)
from random import randint
from math import isclose
from mathutils import Matrix
from random import random

#------------#
# PROPERTIES #
#------------#

class dividerProps(PropertyGroup):
    
    
    int_divisions : IntProperty(
        name = "Number of divisions",
        description = "Set the number of division on the initial plane",
        default = 0,
        min = 0,
        soft_max = 5
        )

    int_iterations : IntProperty(
        name = "Number of iterations",
        description = "Set the number of iterations",
        default = 1,
        min = 1,
        soft_max = 5
        )

    int_plane_size : IntProperty(
        name = "Size of plane",
        description = "Set the size of the initial plane",
        default = 2,
        min = 1,
        soft_max = 10
        )

    int_speed : IntProperty(
        name = "Speed",
        description = "Set the speed of the animation",
        default = 2,
        min = 1,
        soft_max = 10
        )

    float_speed_2nd : FloatProperty(
        name = "Speed of second axis",
        description = "Set the speed of the second axis animation",
        default = 0,
        min = 0,
        max = 3
        )

    float_min_span_x : FloatProperty(
        name = "min_span_x",
        description = "Set the min_span_x",
        default = .5,
        min = 0,
        max = 2
        )

    float_min_span_y : FloatProperty(
        name = "min_span_y",
        description = "Set the min_span_y",
        default = .7,
        min = 0,
        max = 2
        )

    float_max_span_x : FloatProperty(
        name = "max_span_x",
        description = "Set the max_span_x",
        default = 1.5,
        min = 0,
        max = 2
        )

    float_max_span_y : FloatProperty(
        name = "max_span_y",
        description = "Set the max_span_y",
        default = 1.4,
        min = 0,
        max = 2
        )

    float_scale_factor : FloatProperty(
        name = "scale_factor",
        description = "Set the scale_factor",
        default = .95,
        min = 0,
        max = 1
        )

    bool_alternate_calc : BoolProperty(
        name = "Alternate Calculation",
        description = "Alternate Calculation",
        default = False
        )

    bool_alternate_calc2 : BoolProperty(
        name = "Alternate Calculation 2",
        description = "Alternate Calculation 2",
        default = False
        )
        
    int_percentx : IntProperty(
        name = "X value",
        description = "Set the X value",
        default = 27,
        min = 0,
        soft_max = 100
        )

    int_percenty : IntProperty(
        name = "Y value",
        description = "Set the Y value",
        default = 13,
        min = 0,
        soft_max = 100
        )

    int_seed : IntProperty(
        name = "Seed",
        description = "Set the seed for the division",
        default = 123,
        min = 1,
        soft_max = 1000
        )

    float_noisestrength : FloatProperty(
        name = "Noise Strength",
        description = "Set the noise strength",
        default = 0,
        min = 1,
        max = 1
        )

    float_noiseloop : FloatProperty(
        name = "Noise Loop",
        description = "Set the noise Loop",
        default = 1,
        min = 0,
        soft_max = 100
        )
        
    float_noisefreq : FloatProperty(
        name = "Noise Frequency",
        description = "Set the noise frequency",
        default = 1,
        min = 1,
        soft_max = 5
        )

    bool_create_dupliface : BoolProperty(
        name = "Cube and dupliface",
        description = "Create cube, parent it and enable dupliface",
        default = True
        )
        
    bool_create_modifiers : BoolProperty(
        name = "Create modifiers",
        description = "Create modifiers with mask texture",
        default = True
        )
 

#----#
# UI #
#----#

class dividerPanel(bpy.types.Panel):
    # Creates a Panel in the sidebar
    bl_label = "divider"
    bl_idname = "OBJECT_PT_divider"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "divider"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column(align=False)
        
        
        col.prop(scene.rg_props, "int_divisions")
        col.separator()
        col.prop(scene.rg_props, "int_iterations")
        col.separator()
        col.prop(scene.rg_props, "int_speed")
        col.separator()
        col.prop(scene.rg_props, "float_speed_2nd")
        col.separator()
        col.prop(scene.rg_props, "int_plane_size")
        col.separator()
        col.prop(scene.rg_props, "float_scale_factor", slider = True)
        col.separator()
        col.prop(scene.rg_props, "float_min_span_x", slider = True)
        col.separator()
        col.prop(scene.rg_props, "float_max_span_x", slider = True)
        col.separator()
        col.prop(scene.rg_props, "float_min_span_y", slider = True)
        col.separator()
        col.prop(scene.rg_props, "float_max_span_y", slider = True)
        col.separator()
        col.prop(scene.rg_props, "bool_alternate_calc")
        col.separator()
        col.prop(scene.rg_props, "bool_alternate_calc2")
        col.separator()        

        col.separator()
        
                
        sub = col.row()
        sub.scale_y = 2.0
        sub.operator("wm.divider")
        


#----------#
# OPERATOR #
#----------#

class divider(bpy.types.Operator):
    # RandoGrid Operator
    bl_idname = "wm.divider"
    bl_label = "CREATE DIVIDER"
    
    
    def execute(self, context):
            
        rgp = bpy.context.scene.rg_props
            
        speed = rgp.int_speed
        speed_2nd = rgp.float_speed_2nd
        plane_size = rgp.int_plane_size
        nb_divide = rgp.int_divisions
        min_span_x = rgp.float_min_span_x
        max_span_x = rgp.float_max_span_x
        min_span_y = rgp.float_min_span_y
        max_span_y = rgp.float_max_span_y
        scale_factor = rgp.float_scale_factor
        iterations = rgp.int_iterations
        alternate_calc = rgp.bool_alternate_calc
        alternate_calc2 = rgp.bool_alternate_calc2
        
    #---------------------------#
    # Get Plugin parameters     #
    # Issue with mathutil.noise #
    #---------------------------#
        ###########
        #BMESH FROM DATA
        ###########

        def bmesh_from_pydata(bm, verts=None, edges=None, faces=None):

            if not verts:
                return bm

            add_vert = bm.verts.new

            bm_verts = [add_vert(co) for co in verts]
            bm.verts.index_update()

            if faces:
                add_face = bm.faces.new
                for face in faces:
                    add_face([bm_verts[i] for i in face])
                bm.faces.index_update()

            if edges:
                add_edge = bm.edges.new
                for edge in edges:
                    print("edge ",edge) 
                    edge_seq = bm_verts[edge[0]], bm_verts[edge[1]]
                    try:
                        add_edge(edge_seq)
                    except ValueError:
                        # edge exists!
                        print("edge exists")
                        pass
                bm.edges.index_update()

            return bm

        ###########
        #VERTICE CALC
        ###########

        def  vertice_calc(shift_x,shift_y,min_x,min_y,max_x,max_y):

            half_x = (max_x-min_x)/2
            half_y = (max_y-min_y)/2

            # 3----8/9-----2
            # |     |     |
            # |     |     |
            # |   14/15--6/7
            # 10/11-12/13 |
            # |     |     |
            # |     |     | 
            # 0----4/5----1

            verts_calc = [
                (min_x, min_y, 0),
                (max_x, min_y, 0),
                (max_x, max_y, 0),
                (min_x, max_y, 0),
                (min_x+(half_x*shift_x), min_y, 0),
                (min_x+(half_x*shift_x), min_y, 0),
                (max_x, min_y+(half_y*shift_y), 0),
                (max_x, min_y+(half_y*shift_y), 0),
                (min_x+(half_x*shift_x), max_y, 0),
                (min_x+(half_x*shift_x), max_y, 0),
                (min_x, min_y+(half_y*(2-shift_y)), 0),
                (min_x, min_y+(half_y*(2-shift_y)), 0),
                (min_x+(half_x*shift_x), min_y+(half_y*(2-shift_y)), 0),
                (min_x+(half_x*shift_x), min_y+(half_y*(2-shift_y)), 0),
                (min_x+(half_x*shift_x), min_y+(half_y*shift_y), 0),
                (min_x+(half_x*shift_x), min_y+(half_y*shift_y), 0)
                ]
                
            return verts_calc

        ###########
        #POLYGON CUT
        ###########

        def polygon_cut(bm,a,b,c,d,e,f):
            
            # 3----8/9-----2
            # |     |     |
            # |     |     |
            # |   14/15--6/7
            # 10/11-12/13 |
            # |     |     |
            # |     |     | 
            # 0----4/5----1

            faces = [
            (0, 4, 12, 10),
            (11, 13, 8, 3),
            (14, 6, 2, 9),
            (5, 1, 7, 15)
            ]
            
            verts_calc = vertice_calc(a,b,c,d,e,f)
            bmesh_from_pydata(bm, verts_calc,[], faces)
            


        ###########
        #FLUSH MESH
        ###########

        def flush_mesh(nb_divide, plane_size):

            ####Block user = 1 -> Mesh is linked  
            for block in bpy.data.meshes:
                if block.users == 0:
                    bpy.data.meshes.remove(block)
                 
            if not ("dividermesh" in bpy.data.meshes):
                print("dividermesh initial creation")
                mesh = bpy.data.meshes.new("dividermesh")  # add a new mesh
                obj = bpy.data.objects.new("Divider", mesh)  # add a new object using the mesh
                scene = bpy.context.scene
                scene.collection.objects.link(obj) 
                bpy.context.view_layer.objects.active = obj
    
            bm = bmesh.new()
            me = bpy.data.meshes['dividermesh']
            bm.from_mesh(me)
            bm.clear()

            print("dividermesh create plane")
            mesh = bpy.data.meshes['dividermesh']
            obj = bpy.data.objects['Divider']
            
            verts = [( plane_size,  plane_size,  0.0), 
                    ( plane_size, -plane_size,  0.0),
                    (-plane_size, -plane_size,  0.0),
                    (-plane_size,  plane_size,  0.0),
                    ]  # 4 verts made with XYZ coords
            edges = []
            faces = [[0, 1, 2, 3]]
            bmesh_from_pydata(bm, verts, edges, faces)
            bm.edges.ensure_lookup_table()
            bmesh.ops.subdivide_edges(bm,
                edges=bm.edges,
                use_grid_fill=True,
                cuts=nb_divide)
            bm.to_mesh(me)
            bm.free()

            mesh.update()


        ###########
        #MAP RANGE
        ###########

        def translate(value, leftMin, leftMax, rightMin, rightMax):
            # Figure out how 'wide' each range is
            leftSpan = leftMax - leftMin
            rightSpan = rightMax - rightMin
            # Convert the left range into a 0-1 range (float)
            valueScaled = float(value - leftMin) / float(leftSpan)
            # Convert the 0-1 range into a value in the right range.
            return rightMin + (valueScaled * rightSpan)


        ###########
        #POLY CUT
        ###########
        def execute_cut(scene):
            
            first_frame = bpy.context.scene.frame_start
            last_frame = bpy.context.scene.frame_end
            current_frame = bpy.context.scene.frame_current
            nb_fame = last_frame - first_frame + 1
            var_sinus = (math.sin(math.radians(current_frame*((360*speed)/nb_fame)))+1)/2
            if alternate_calc2:
                var_cosinus = (math.sin(math.radians(current_frame*(((360-speed_2nd*90)*speed)/nb_fame)))+1)/2
            else:
                var_cosinus = (math.cos(math.radians(current_frame*(((360-speed_2nd*90)*speed)/nb_fame)))+1)/2
            
            flush_mesh(nb_divide,plane_size)
            
            bm = bmesh.new()
            me = bpy.data.meshes['dividermesh']
            bm.from_mesh(me)
            bm.faces.ensure_lookup_table()
            face_select = list(bm.faces)
            seed = 0
            for iter in range(iterations):
                print("iteration :", iter)
                face_select = list(bm.faces)
                for f in list(bm.faces):
                    bm.faces.ensure_lookup_table()
                    if f.is_valid:
                        for co in list(f.verts):
                            minX = min(co.co.x for co in f.verts)
                            maxX = max(co.co.x for co in f.verts)
                            minY = min(co.co.y for co in f.verts)
                            maxY = max(co.co.y for co in f.verts)     
                        if alternate_calc:
                            #METHODE 1
                            shift_x = translate(var_sinus,0,1,min_span_x,max_span_x)
                            shift_y = translate(var_cosinus,0,1,min_span_y,max_span_y)
                        else:
                            #METHODE 2
                            noise_x = math.sin(f.index) + seed + 1
                            noise_y = math.cos(f.index) + seed + 0
                            noise_coord = (noise_x,noise_y,0)
                            noise = mathutils.noise.noise(noise_coord)
                            range_noise = translate(noise, -.5,.5,0,1)
                            print("range noise", translate(noise, -.5,.5,0,1))
                            if (f.index%2 == 0):
                                shift_x = translate(var_cosinus+range_noise,0,2,min_span_x,max_span_x)
                                shift_y = translate(var_sinus+(1-range_noise),0,2,min_span_y,max_span_y)
                            else:
                                shift_x = translate(var_sinus+range_noise,0,2,min_span_x,max_span_x)
                                shift_y = translate(var_cosinus+(1-range_noise),0,2,min_span_y,max_span_y)
                        if (f.index%2 == 0):
                            polygon_cut(bm,shift_x,shift_y,minX,minY,maxX,maxY)
                        else:
                            polygon_cut(bm,shift_y,shift_x,minX,minY,maxX,maxY)
                bmesh.ops.delete(bm, geom=face_select, context='FACES')    
            for fa in bm.faces:
                bmesh.ops.scale(bm,
                vec = (scale_factor,) * 3,
                space = Matrix.Translation(-fa.calc_center_median()),
                verts = fa.verts)
                clayers = bm.loops.layers.color
                color_layer = clayers.get('vertcolor') or clayers.new('vertcolor')
                for lo in fa.loops:
                    lo[color_layer] = (abs(math.sin(fa.index)),0,0,0)
            bm.to_mesh(me)
            me.update()
            mymesh = bpy.data.meshes['dividermesh']
            mypolys = mymesh.polygons
            for p in mypolys:
                p.use_smooth = True



        bpy.app.handlers.frame_change_post.clear()
        bpy.app.handlers.frame_change_post.append(execute_cut)

        return {'FINISHED'}




#----------#
# REGISTER #
#----------#

def register():
    bpy.utils.register_class(dividerPanel)
    bpy.utils.register_class(divider)
    bpy.utils.register_class(dividerProps)
    bpy.types.Scene.rg_props = PointerProperty(type=dividerProps)

def unregister():
    bpy.utils.unregister_class(dividerPanel)
    bpy.utils.unregister_class(divider)
    bpy.utils.unregister_class(dividerProps)
    del bpy.types.Scene.rg_props

if __name__ == "__main__":
    register()
