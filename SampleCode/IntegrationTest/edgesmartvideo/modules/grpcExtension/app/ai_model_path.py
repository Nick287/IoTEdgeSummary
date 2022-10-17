class AI_Model_Path_Class(object):
    MODEL_FULL_PATH = ""
    MODEL_LABELMAP = ""

    def Get_Labelmap_Path(self):
        return self.MODEL_LABELMAP
    
    def Set_Labelmap_Path(self, newPath):
        self.MODEL_LABELMAP = newPath

    def Get_Model_Path(self):
        return self.MODEL_FULL_PATH
    
    def Set_Model_Path(self, newPath):
        self.MODEL_FULL_PATH = newPath

AI_Model_Path = AI_Model_Path_Class()