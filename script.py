bl_info = {
    "name": "3D Ripper DX Adjustments",
    "description": "Fixes xscale, yscale, zscale, texture paths and materials",
    "category": "Mesh",
    "version": (0, 2),
    "blender": (2, 83, 0),
    "author": "Xyoz Netsphere",
    #"location": 
    "support": "COMMUNITY"
}

import bpy
import re
import os
from bpy.props import FloatProperty, StringProperty

class RipperDXPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "3D Ripper DX"
    bl_label = "3D Ripper DX S4L"

    bpy.types.Scene.ripperdx_xscale = FloatProperty(
            name="X",
            description="x Scale",
            min=-100.0, max=100.0,
            default=1.000,
            precision=3
            )
    bpy.types.Scene.ripperdx_yscale = FloatProperty(
            name="Y",
            description="y Scale",
            min=-100.0, max=100.0,
            default=1.000,
            precision=3
            )
    bpy.types.Scene.ripperdx_zscale = FloatProperty(
            name="Z",
            description="z Scale",
            min=-100.0, max=100.0,
            default=1.000,
            precision=3
            )
    bpy.types.Scene.ripperdx_targetprefix= StringProperty(
            name = "Prefix",
            default = "DrawCall",
            description = "Define the prefix of all meshes you want to target",
            )
    bpy.types.Scene.ripperdx_sourceobj = StringProperty(
            name = "Source *.obj",
            default = "",
            description = "Define the path to the .obj you have imported",
            subtype = 'FILE_PATH'
            )
    bpy.types.Scene.ripperdx_texture_root= StringProperty(
            name = "Texture Path",
            default = "",
            description = "Define the texture folder",
            subtype = 'DIR_PATH'
            )
    bpy.types.Scene.ripperdx_specular = FloatProperty(
            name="Intensity:",
            description="y Scale",
            min=0.0, max=1.0,
            default=0.0,
            precision=3
            )

    def draw(self, context):
        layout = self.layout;
        row = layout.column()
        row.prop(context.scene, 'ripperdx_sourceobj')
        row.operator("script.ripperdx_importvalues", text="Import Scalings")
        row = layout.column(align=True)
        row.prop(context.scene, 'ripperdx_xscale')
        row.prop(context.scene, 'ripperdx_yscale')        
        row.prop(context.scene, 'ripperdx_zscale')
        row.operator("mesh.ripperdx_fixscale", text="Adjust Scaling")
        row = layout.column()	
        row.prop(context.scene, 'ripperdx_texture_root')
        row.operator("mesh.ripperdx_fixtextures", text="Fix Textures")
        row = layout.column(align=True)	
        row.prop(context.scene, 'ripperdx_specular')
        row.operator("mesh.ripperdx_fixspecular", text="Adjust Specular")

class RipperDXImportValues(bpy.types.Operator):
    bl_idname = "script.ripperdx_importvalues"
    bl_label = "Import Values from obj"
    bl_options = {'REGISTER'}
    def invoke(self, context, event):
        appdata = os.getenv('APPDATA')
        
        if bpy.context.scene['ripperdx_sourceobj'] != "":
             try:
                 with open(bpy.path.abspath(bpy.context.scene['ripperdx_sourceobj'])) as f:
                     line = f.readline()
                     line = line[1:line.find('#',1)]
                     with open(appdata + 'line.txt', 'w') as r:
                         r.write(line)
                     result = re.search('(?P<xscale>Xscale:[^.]*\.[^,]*).*?(?P<yscale>Yscale:[^.]*\.[^,]*).*?(?P<zscale>Zscale:[^.]*\.[^\s#]*)',line)
                     with open(appdata + 'lresultf.txt', 'w') as r:
                         r.write(result.group('xscale')[7:] + '\n' + result.group('yscale')[7:] + '\n' + result.group('zscale')[7:])
                     bpy.context.scene['ripperdx_xscale'] = float(result.group('xscale')[7:])
                     bpy.context.scene['ripperdx_yscale'] = float(result.group('yscale')[7:])
                     bpy.context.scene['ripperdx_zscale'] = float(result.group('zscale')[7:])*-1
             except KeyError:
                 pass
        return {"FINISHED"}
                     
                     

class RipperDXFixScale(bpy.types.Operator) :
    bl_idname = "mesh.ripperdx_fixscale"
    bl_label = "Fix Scaling"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        for obj in bpy.data.objects:
            if obj.name[:8] == 'DrawCall':
                try:
                    obj.scale[0] = bpy.context.scene['ripperdx_xscale']
                except KeyError:
                    pass
                try:
                    obj.scale[1] = bpy.context.scene['ripperdx_yscale']
                except KeyError:
                    pass
                try:
                    obj.scale[2] = bpy.context.scene['ripperdx_zscale']
                except KeyError:
                    pass

        return {"FINISHED"}

class RipperDXFixTextures(bpy.types.Operator) :
    bl_idname = "mesh.ripperdx_fixtextures"
    bl_label = "Fix Scaling"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        if bpy.context.scene['ripperdx_texture_root'] != '':
            for img in bpy.data.images:
                if img.filepath.find('\\') == -1 and img.filepath.find('/') == -1:
                    img.filepath = bpy.context.scene['ripperdx_texture_root'] + img.filepath
                    img.reload()
                img.reload()
        return {"FINISHED"}

class RipperDXFixSpecular(bpy.types.Operator) :
    bl_idname = "mesh.ripperdx_fixspecular"
    bl_label = "Fix Specular"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        for mat in bpy.data.materials:
            try:
                mat.specular_intensity =  bpy.context.scene['ripperdx_specular']
            except KeyError:
                mat.specular_intensity =  0
                pass
        return {"FINISHED"}

def register():
    bpy.utils.register_class(RipperDXPanel)
    bpy.utils.register_class(RipperDXFixScale)
    bpy.utils.register_class(RipperDXFixTextures)
    bpy.utils.register_class(RipperDXFixSpecular)
    bpy.utils.register_class(RipperDXImportValues)

def unregister():
    bpy.utils.unregister_class(RipperDXPanel)
    bpy.utils.unregister_class(RipperDXFixScale)
    bpy.utils.unregister_class(RipperDXFixTextures)
    bpy.utils.unregister_class(RipperDXFixSpecular)
    bpy.utils.unregister_class(RipperDXImportValues)

if __name__ == "__main__":
    register()
