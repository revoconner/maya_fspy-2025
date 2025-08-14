"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

Usage:
    import maya_fspy.ui as mfspy_ui
    mfspy_ui.maya_fspy_ui()

Note that you will nee to set the correct axes inside of the standalone fspy application for the best results.
Vanishing point axes:
    1. -Z
    2. -X
Reference distance:
    Along the y-axis
"""
import os
from functools import partial

import maya.cmds as cmds

from .core import create_camera_and_plane

__author__ = 'Justin Pedersen'
__version__ = '1.2.0'

WINDOW_NAME = "fspyImporter"
WINDOW_TITLE = "Fspy Importer - v{}".format(__version__)


def close_existing_windows():
    """
    Close any existing instances of the maya fspy window
    """
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME, window=True)


class FSpyImporter:
    """
    Main UI Class for the importer
    """
    def __init__(self):
        self.window = None
        self.json_field = None
        self.image_field = None
        
        self.create_ui()

    def create_ui(self):
        """
        Create the main UI
        """
        # Close existing window if it exists
        close_existing_windows()
        
        # Create main window
        self.window = cmds.window(WINDOW_NAME, 
                                  title=WINDOW_TITLE, 
                                  widthHeight=(350, 120),
                                  resizeToFitChildren=True)
        
        # Main column layout
        main_layout = cmds.columnLayout(adjustableColumn=True, 
                                        columnAttach=('both', 5),
                                        rowSpacing=5,
                                        columnWidth=340)
        
        # JSON file browser
        self.json_field = cmds.textFieldButtonGrp(
            label='JSON:', 
            text='',
            buttonLabel='Browse',
            columnWidth3=[60, 200, 70],
            buttonCommand=partial(self.browse_json_file)
        )
        
        # Image file browser  
        self.image_field = cmds.textFieldButtonGrp(
            label='Image:', 
            text='',
            buttonLabel='Browse',
            columnWidth3=[60, 200, 70],
            buttonCommand=partial(self.browse_image_file)
        )
        
        # Separator
        cmds.separator(height=10, style='in')
        
        # Import button
        cmds.button(label='Import', 
                    height=30,
                    command=partial(self.generate_camera))
        
        # Show window
        cmds.showWindow(self.window)

    def browse_json_file(self, *args):
        """
        Open file dialog for JSON files
        """
        file_filter = "JSON Files (*.json);;All Files (*.*)"
        file_path = cmds.fileDialog2(
            fileMode=1,
            caption="Select JSON File",
            fileFilter=file_filter
        )
        
        if file_path:
            cmds.textFieldButtonGrp(self.json_field, edit=True, text=file_path[0])

    def browse_image_file(self, *args):
        """
        Open file dialog for image files
        """
        all_image_formats = ['psd', 'als', 'avi', 'dds', 'gif', 'jpg', 'cin', 'iff', 'exr',
                             'png', 'eps', 'yuv', 'hdr', 'tga', 'tif', 'tim', 'bmp', 'xpm']
        file_filter = 'All Image Files (*.{});;All Files (*.*)'.format(' *.'.join([x for x in all_image_formats]))
        
        file_path = cmds.fileDialog2(
            fileMode=1,
            caption="Select Image File", 
            fileFilter=file_filter
        )
        
        if file_path:
            cmds.textFieldButtonGrp(self.image_field, edit=True, text=file_path[0])

    def generate_camera(self, *args):
        """
        Main function to generate the camera and image plane from UI.
        """
        json_path = cmds.textFieldButtonGrp(self.json_field, query=True, text=True)
        image_path = cmds.textFieldButtonGrp(self.image_field, query=True, text=True)
        
        # Validate JSON file
        if not json_path or os.path.splitext(json_path)[-1].lower() != '.json':
            cmds.warning('The JSON field only accepts .json file formats')
            return
        
        # Validate image file
        if not image_path:
            cmds.warning('Please set an image path.')
            return
            
        # Validate both files exist
        if not os.path.exists(json_path):
            cmds.warning('JSON file does not exist: {}'.format(json_path))
            return
            
        if not os.path.exists(image_path):
            cmds.warning('Image file does not exist: {}'.format(image_path))
            return
        
        # Create camera and image plane
        try:
            result = create_camera_and_plane(json_path, image_path)
            cmds.confirmDialog(
                title='Success',
                message='Camera and image plane created successfully!',
                button=['OK']
            )
        except Exception as e:
            cmds.warning('Error creating camera: {}'.format(str(e)))


def maya_fspy_ui():
    """
    Open the maya fspy ui.
    """
    fspy_importer = FSpyImporter()
    return fspy_importer
