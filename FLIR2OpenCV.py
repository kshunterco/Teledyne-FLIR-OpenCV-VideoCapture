# coding=utf-8
#
# Object that kind of works like cv2.VideoCapture object, based on code from
# PySpin (Spinnaker) AcquireAndDisplay.py

from os import environ
import PySpin
from cv2 import cvtColor, COLOR_GRAY2RGB
from lib.tracking import clean_exit # This is also defined below

environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

class FLIR_cam:
    def __init__(self):
        # Retrieve singleton reference to system object
        self.system = PySpin.System.GetInstance()
        version = self.system.GetLibraryVersion()
        print('[INFO] FLIR Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

        # Retrieve list of cameras from the system
        self.cam_list = self.system.GetCameras()
        if self.cam_list.GetSize() == 0:
            self.cam = None
            self.close_camera()
            print('[ERROR] Not any cameras!')
            clean_exit()
        self.nodemap_tldevice = None
        self.nodemap = None
        self.cam = self.cam_list[0] # we only have one cam!!
        ret = self.init_camera()
        if not ret:
            print('[ERROR] Camera initialization failed')
            clean_exit()
    def init_camera(self):
        """ please see NodeMapInfo example for more in-depth comments on
            setting up cameras. """
        try:
            self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
            self.cam.Init()
            self.nodemap = self.cam.GetNodeMap()
            ret = setup_acqusition(self.cam, self.nodemap, self.nodemap_tldevice)
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            ret = False
        return ret
    def acquire_image(self):
        try:
            image_result = self.cam.GetNextImage(1000)
            if image_result.IsIncomplete():
                print('[INFO] Image incomplete with image status %d ...' % image_result.GetImageStatus())
            else:                    
                image_data = image_result.GetNDArray()                
            image_result.Release()
            return cvtColor(image_data, COLOR_GRAY2RGB)
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
    def close_camera(self):
        # Release reference to camera
        # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
        # cleaned up when going out of scope.
        # The usage of del is preferred to assigning the variable to None.
        if self.cam is not None:
            self.cam.EndAcquisition()
            self.cam.DeInit()
            del self.cam
        self.cam_list.Clear()
        self.system.ReleaseInstance()
        print('[INFO] FLIR system instance released...')
        
def setup_acqusition(cam, nodemap, nodemap_tldevice):
    """ This function sets up a device for continuous acquisition """
    sNodemap = cam.GetTLStreamNodeMap()

    # Change bufferhandling mode to NewestOnly
    node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
    if not PySpin.IsReadable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
        print('[ERROR] Unable to set stream buffer handling mode.. Aborting...')
        return False

    # Retrieve entry node from enumeration node
    node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
    if not PySpin.IsReadable(node_newestonly):
        print('[ERROR] Unable to set stream buffer handling mode.. Aborting...')
        return False

    # Retrieve integer value from entry node
    node_newestonly_mode = node_newestonly.GetValue()

    # Set integer value from entry node as new value of enumeration node
    node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

    #print('*** IMAGE ACQUISITION ***\n')
    try:
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsReadable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('[ERROR] Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsReadable(node_acquisition_mode_continuous):
            print('[ERROR] Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        #print('Acquisition mode set to continuous...')

        #  Begin acquiring images
        cam.BeginAcquisition()

        #print('Acquiring images...')

        #  Retrieve device serial number for filename
        #
        #  *** NOTES ***
        #  The device serial number is retrieved in order to keep cameras from
        #  overwriting one another. Grabbing image IDs could also accomplish
        #  this.
        device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('[INFO] Device serial number retrieved as %s...' % device_serial_number)

    except PySpin.SpinnakerException as ex:
        print('[ERROR] %s' % ex)
        return False
    
    return True

''' Imported function definition '''
# from sys import exit as sysexit
# from cv2 import destroyAllWindows

# def clean_exit():
#     """ Cleanly exit """
#     destroyAllWindows()
#     sysexit()
