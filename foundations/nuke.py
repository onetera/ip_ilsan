import os
import __builtin__
from globals.constants import Constants


__all__ = ['open', 'Error']

CODEC  = {
    'H.264': 'avc1',
    'Photo-JPEG': 'jpeg',
    'Apple ProRes 422':'apcn',
    'Apple ProRes 422 (HQ)':'apch',
    'Apple ProRes 422 (LT)':'apcs'
    }
CODEC_FILENAME = Constants.codecFile

class Error(Exception):
    pass

class Nuke:
    def __init__(self, template):
        self._template = __builtin__.open(template)

    def set_source(self, path):
        self._source = path
        self._extension = os.path.splitext(path)[1]

    def set_destination(self, path):
        self._destination = path

    def set_codec(self, codec):
        self._codec = codec

    def set_slate(self, state):
        self._slate_is_checked = state

    def set_note(self, note):
        self._note = note

    def set_username(self, username):
        self._username = username

    def set_date(self, state, date):
        self._date_is_checked = state
        self._date = date

    def set_frame(self, state, frame):
        self._frame_is_checked = state
        self._frame = frame

    def set_lut(self, state, lut):
        self._lut_is_checked = state
        self._lut = lut

    def set_quality(self, quality):
        q = {
             'Best':['Lossless', 4],
             'High':['High', 3],
             'Medium':['Normal', 2]
             }
        self._quality = q[quality][0]
        self._quality_level = q[quality][1]

    def set_fps(self, fps):
        # special codec
        if self._codec == 'Apple ProRes 422 (HQ)' or self._codec == 'Apple ProRes 422 (LT)':
            settings = self.getCodecList(CODEC_FILENAME)['Apple ProRes 422'][fps]
            settings_l = list(settings)
            if self._codec == 'Apple ProRes 422 (HQ)':
                settings_l[160:162] = ['6', '8']
            elif self._codec == 'Apple ProRes 422 (LT)':
                settings_l[160:162] = ['7', '3']
            self._settings = ''.join(settings_l)
        else:
            self._settings = self.getCodecList(CODEC_FILENAME)[self._codec][fps]
        self._fps_normal = fps
        if fps == '23.98':
            fps = '23.97999954'
        if fps == '29.97':
            fps = '29.96999931'
        if fps == '59.94':
            fps = '59.93999863'
        self._fps = fps

    def set_format(self, width, height, ratio, name):
        self._format = ' format "%(width)s %(height)s 0 0 %(width)s %(height)s %(ratio)s %(name)s"' % {
            'width': width,
            'height': height,
            'ratio': ratio,
            'name': name
            }

    def set_opacity(self, opacity):
        self._opacity = opacity

    def set_frame_range(self, frame):
        self._first_frame, self._last_frame = frame.split('-')

    ############
    # new node
    ###########
    def set_shotname(self, shotname):
        self._shotname = shotname

    def set_version(self, version):
        self._version = version

    def set_cgi_version(self, version):
        self._cgi_version = version

    def set_jobname(self, jobname):
        self._jobname = jobname

    def set_task(self, task):
        self._task = task

    def set_aspect_ratio(self, aspect_ratio):
        self._aspect_ratio = aspect_ratio

    def set_filelog(self, filelogo):
        self._filelogo = filelogo

    def set_status(self, status):
        self._status = status

    def set_tempdir(self, dir):
        self._tempdir = dir

    def set_proxy_file(self, filename):
        self._proxy_file = filename
        
    def set_scale(self ,scale):
        self._scale = scale

    def script_test(self):
        lines = self._template.readlines()
        found = False
        buf = {}
        temp = {}
        item = ''
        name = ''
        root = ''
        for line, row in enumerate(lines):
            try:
                token = row.split()[0]
            except IndexError:
                return None
                break
            if token == 'Write' or token == 'Root':
                root = token
                temp[token] = {}
                item = token
                found = True
                continue

            if found and token == '}':
                found = False
                #if name.find('Write') != -1:
                #    continue
                if root == 'Write':
                    node = temp['Write']['name']
                    temp[node] = temp['Write']
                    del temp['Write']
                buf.update(temp)
                temp = {}

            if found:
                if token == 'name':
                    name = row.strip().split(' ',1)[1]
                #temp[item][token] = line
                temp[item][token] = row.split()[1]

        return buf

    def script(self):
        lines = self._template.readlines()
        found = False
        buf = {}
        temp = {}
        item = ''
        name = ''
        root = ''
        for line, row in enumerate( lines):
            token = row.split()[0]
            if (token == 'Read' or token == 'idea_slate' or
                token == 'Root' or token == 'Vectorfield' or
                token == 'Write'):
                root = token
                temp[token] = {}
                item = token
                found = True
                continue

            if found and token == '}':
                found = False

                if item == 'Write' or item == 'Read':
                    temp[name] = temp[item]
                    del temp[item]

                buf.update(temp)
                temp = {}

            if found:
                if token == 'name':
                    name = row.strip().split(' ',1)[1]
                temp[item][token] = line

        ##########################
        # idea_slate
        ##########################
        idx = buf['idea_slate']['plate_shotname']
        lines[idx] = ' plate_shotname "%s"\n' % self._shotname
        idx = buf['idea_slate']['plate_version']
        lines[idx] = ' plate_version %s\n' % self._version
        idx = buf['idea_slate']['plate_jobname']
        lines[idx] = ' plate_jobname "%s"\n' % self._jobname
        idx = buf['idea_slate']['plate_task']
        lines[idx] = ' plate_task "%s"\n' % self._task
        idx = buf['idea_slate']['plate_artist']
        lines[idx] = ' plate_artist "%s"\n' % self._username
        idx = buf['idea_slate']['CustomStatus']
        lines[idx] = ' CustomStatus "%s"\n' % self._status
        idx = buf['idea_slate']['plate_description1']
        lines[idx] = ' plate_description1 "%s"\n' % self._note
        idx = buf['idea_slate']['MaskAspectRatio']
        lines[idx] = ' MaskAspectRatio %s\n' % self._aspect_ratio
        idx = buf['idea_slate']['MaskOpacity']
        lines[idx] = ' MaskOpacity %s\n' % self._opacity
        idx = buf['idea_slate']['ver']
        lines[idx] = ' ver %s\n' % self._cgi_version
        idx = buf['idea_slate']['scale']
        lines[idx] = ' scale %s\n' % self._scale
        #idx = buf['idea_slate']['TypeSize']
        #lines[idx] = ' TypeSize %s\n' % 
        # hide overlay
        if not self._slate_is_checked:
            idx = buf['idea_slate']['ypos']
            lines[idx] = '%s disable true' % lines[idx]
            #idx = buf['idea_slate']['Overlays']
            #lines[idx] = '%s BurnIOverlays false\n' % lines[idx]
            #idx = buf['idea_slate']['MaskOverlay']
            #lines[idx] = '%s MaskOn false\n' % lines[idx]

        ##########################
        # Root
        ##########################
        idx = buf['Root']['format']
        lines[idx] = self._format
        idx = buf['Root']['last_frame']
        lines[idx] = ' last_frame %s\n' % self._last_frame
        try:
            idx = buf['Root']['first_frame']
            lines[idx] = ' first_frame %s\n' % self._first_frame
        except:
            idx = buf['Root']['last_frame']
            lines[idx] = ' first_frame %s\n%s' % (self._first_frame, lines[idx])
        try:
            idx = buf['Root']['fps']
            lines[idx] = ' fps %s\n' % self._fps_normal
        except:
            idx = buf['Root']['lock_range']
            lines[idx] = '%s fps %s\n' % (lines[idx], self._fps_normal)
        ##########################
        # Read
        ##########################
        idx = buf['SOURCE']['file']
        lines[idx] = ' file %s\n' % self._source
        idx = buf['SOURCE']['last']
        lines[idx] = ' last %s\n' % self._last_frame
        try:
            idx = buf['SOURCE']['first']
            lines[idx] = ' first %\n' % self._first_frame
        except:
            idx = buf['SOURCE']['last']
            lines[idx] = ' first %s\n%s' % (self._first_frame, lines[idx])
        ##########################
        # Vectorfield
        ##########################
        idx = buf['Vectorfield']['colorspaceIn']
        if (self._extension == '.dpx' or
            self._extension == '.cin'):
            lines[idx] = ' colorspaceIn Cineon\n'
        elif self._extension == '.exr':
            lines[idx] = ' colorspaceIn linear\n'
        else:
            lines[idx] = ' colorspaceIn sRGB\n'
        idx = buf['Vectorfield']['vfield_file']
        lines[idx] = ' vfield_file "%s"\n' % self._lut
        
        if not self._lut_is_checked:
            idx = buf['Vectorfield']['ypos']
            lines[idx] = '%s\n disable true\n' % lines[idx]
        ##########################
        # MOV
        ##########################
        idx = buf['MOV']['file_type']
        if self._extension != '.jpg':
            lines[idx] = ' file_type ffmpeg\n disable true\n'
        idx = buf['MOV']['codec']
        lines[idx] = ' codec %s\n' % CODEC[self._codec]
        try:
            idx = buf['MOV']['fps']
            lines[idx] = ' fps %s\n' % self._fps
        except:
            idx = buf['MOV']['codec']
            lines[idx] = '%s fps %s\n' % (lines[idx], self._fps)
        if self._extension != '.jpg':
            lines[idx] = ''

        idx = buf['MOV']['quality']
        lines[idx] = ' quality %s\n' % self._quality
        if self._extension != '.jpg':
            lines[idx] = ''

        idx = buf['MOV']['settings']
        # change quality value
        settings = list(self._settings) 
        settings[179] = str(self._quality_level)
        lines[idx] = ''.join(settings)
        if self._extension != '.jpg':
            lines[idx] = ''

        if not self._lut_is_checked:
            idx = buf['MOV']['checkHashOnRead']
            lines[idx] = '%s colorspace sRGB\n' % lines[idx]

        idx = buf['MOV']['file']
        lines[idx] = ' file %s\n' % self._destination

        ##########################
        # PROXY
        ##########################
        idx = buf['PROXY']['file']
        lines[idx] = ' file %s\n' % self._destination

        if not self._lut_is_checked:
            idx = buf['PROXY']['checkHashOnRead']
            lines[idx] = '%s colorspace sRGB\n' % lines[idx]

        idx = buf['PROXY']['file']
        lines[idx] = ' file %s\n' % self._proxy_file



        return lines





    def jpg_to_mov_script(self, nukefile):
        template = __builtin__.open(nukefile)
        lines = template.readlines()
        found = False
        buf = {}
        temp = {}
        item = ''
        name = ''
        root = ''
        for line, row in enumerate( lines):
            token = row.split()[0]
            if (token == 'Read' or token == 'Root' or
                token == 'Write'):
                root = token
                temp[token] = {}
                item = token
                found = True
                continue

            if found and token == '}':
                found = False

                if item == 'Write' or item == 'Read':
                    temp[name] = temp[item]
                    del temp[item]

                buf.update(temp)
                temp = {}

            if found:
                if token == 'name':
                    name = row.strip().split(' ',1)[1]
                temp[item][token] = line


        ##########################
        # Root
        ##########################
        idx = buf['Root']['format']
        lines[idx] = self._format
        idx = buf['Root']['last_frame']
        lines[idx] = ' last_frame %s\n' % self._last_frame
        try:
            idx = buf['Root']['first_frame']
            lines[idx] = ' first_frame %s\n' % self._first_frame
        except:
            idx = buf['Root']['last_frame']
            lines[idx] = ' first_frame %s\n%s' % (self._first_frame, lines[idx])
        try:
            idx = buf['Root']['fps']
            lines[idx] = ' fps %s\n' % self._fps_normal
        except:
            idx = buf['Root']['lock_range']
            lines[idx] = '%s fps %s\n' % (lines[idx], self._fps_normal)
        ##########################
        # Read
        ##########################
        idx = buf['SOURCE']['file']
        lines[idx] = ' file %s\n' % self._proxy_file
        idx = buf['SOURCE']['last']
        lines[idx] = ' last %s\n' % self._last_frame
        if self._slate_is_checked:
            first_frame = int(self._first_frame)-1
        else:
            first_frame = int(self._first_frame)
        try:
            idx = buf['SOURCE']['first']
            lines[idx] = ' first %\n' % first_frame
        except:
            idx = buf['SOURCE']['last']
            lines[idx] = ' first %s\n%s' % (first_frame, lines[idx])
        ##########################
        # MOV
        ##########################
        idx = buf['MOV']['codec']
        lines[idx] = ' codec %s\n' % CODEC[self._codec]
        try:
            idx = buf['MOV']['fps']
            lines[idx] = ' fps %s\n' % self._fps
        except:
            idx = buf['MOV']['codec']
            lines[idx] = '%s fps %s\n' % (lines[idx], self._fps)

        idx = buf['MOV']['quality']
        lines[idx] = ' quality %s\n' % self._quality

        idx = buf['MOV']['settings']
        # change quality value
        settings = list(self._settings) 
        settings[179] = str(self._quality_level)
        lines[idx] = ''.join(settings)

        idx = buf['MOV']['file']
        lines[idx] = ' file %s\n' % self._destination

        return lines













    def script_org(self):
        lines = self._template.readlines()
        found = False
        buf = {}
        temp = {}
        item = ''
        name = ''
        for line, row in enumerate( lines):
            token = row.split()[0]
            if (token == 'Read' or token == 'idea_slate' or
                token == 'Root' or token == 'Vectorfield' or
                token == 'Write'):
                temp[token] = {}
                item = token
                found = True
                continue

            if found and token == '}':
                found = False
                if name.find('Read') != -1:
                    continue
                buf.update(temp)
                temp = {}

            if found:
                if token == 'name':
                    name = row.strip().split(' ',1)[1]
                temp[item][token] = line


        ##########################
        # idea_slate
        ##########################
        idx = buf['idea_slate']['plate_shotname']
        lines[idx] = ' plate_shotname "%s"\n' % self._shotname

        idx = buf['idea_slate']['plate_version']
        lines[idx] = ' plate_version %s\n' % self._version

        idx = buf['idea_slate']['plate_jobname']
        lines[idx] = ' plate_jobname "%s"\n' % self._jobname

        idx = buf['idea_slate']['plate_task']
        lines[idx] = ' plate_task "%s"\n' % self._task

        idx = buf['idea_slate']['plate_artist']
        lines[idx] = ' plate_artist "%s"\n' % self._username

        idx = buf['idea_slate']['CustomStatus']
        lines[idx] = ' CustomStatus "%s"\n' % self._status

        idx = buf['idea_slate']['plate_description1']
        lines[idx] = ' plate_description1 "%s"\n' % self._note

        idx = buf['idea_slate']['MaskAspectRatio']
        lines[idx] = ' MaskAspectRatio %s\n' % self._aspect_ratio

        idx = buf['idea_slate']['MaskOpacity']
        lines[idx] = ' MaskOpacity %s\n' % self._opacity

        idx = buf['idea_slate']['ver']
        lines[idx] = ' ver %s\n' % self._cgi_version

        #idx = buf['idea_slate']['filelogo']
        #lines[idx] = ' filelogo'

        # hide overlay
        if not self._slate_is_checked:
            idx = buf['idea_slate']['ypos']
            lines[idx] = '%s disable true' % lines[idx]
            #idx = buf['idea_slate']['Overlays']
            #lines[idx] = '%s BurnIOverlays false\n' % lines[idx]
            #idx = buf['idea_slate']['MaskOverlay']
            #lines[idx] = '%s MaskOn false\n' % lines[idx]

        ##########################
        # Root
        ##########################
        idx = buf['Root']['format']
        lines[idx] = self._format
        idx = buf['Root']['last_frame']
        lines[idx] = ' last_frame %s\n' % self._last_frame
        try:
            idx = buf['Root']['first_frame']
            lines[idx] = ' first_frame %s\n' % self._first_frame
        except:
            idx = buf['Root']['last_frame']
            lines[idx] = ' first_frame %s\n%s' % (self._first_frame, lines[idx])
        try:
            idx = buf['Root']['fps']
            lines[idx] = ' fps %s\n' % self._fps_normal
        except:
            idx = buf['Root']['lock_range']
            lines[idx] = '%s fps %s\n' % (lines[idx], self._fps_normal)
        ##########################
        # Read
        ##########################
        idx = buf['Read']['file']
        lines[idx] = ' file %s\n' % self._source
        idx = buf['Read']['last']
        lines[idx] = ' last %s\n' % self._last_frame
        try:
            idx = buf['Read']['first']
            lines[idx] = ' first %\n' % self._first_frame
        except:
            idx = buf['Read']['last']
            lines[idx] = ' first %s\n%s' % (self._first_frame, lines[idx])
        ##########################
        # Vectorfield
        ##########################
        idx = buf['Vectorfield']['colorspaceIn']
        if (self._extension == '.dpx' or
            self._extension == '.cin'):
            lines[idx] = ' colorspaceIn Cineon\n'
        elif self._extension == '.exr':
            lines[idx] = ' colorspaceIn linear\n'
        else:
            lines[idx] = ' colorspaceIn sRGB\n'
        idx = buf['Vectorfield']['vfield_file']
        lines[idx] = ' vfield_file "%s"\n' % self._lut
        
        if not self._lut_is_checked:
            idx = buf['Vectorfield']['ypos']
            lines[idx] = '%s\n disable true\n' % lines[idx]

        ##########################
        # Write
        ##########################
        idx = buf['Write']['codec']
        lines[idx] = ' codec %s\n' % CODEC[self._codec]
        try:
            idx = buf['Write']['fps']
            lines[idx] = ' fps %s\n' % self._fps
        except:
            idx = buf['Write']['codec']
            lines[idx] = '%s fps %s\n' % (lines[idx], self._fps)

        # special codec
        if (self._codec == 'Apple ProRes 422' or
            self._codec == 'Apple ProRes 422 (HQ)' or
            self._codec == 'Apple ProRes 422 (LT)'):
            idx = buf['Write']['settings']
            lines[idx] = self._settings
        else:
            idx = buf['Write']['quality']
            lines[idx] = ' quality %s\n' % self._quality

            idx = buf['Write']['settings']
            # change quality value
            settings = list(self._settings)
            settings[179] = str(self._quality_level)
            #lines[idx] = self._settings
            lines[idx] = ''.join(settings)

        if not self._lut_is_checked:
            idx = buf['Write']['checkHashOnRead']
            lines[idx] = '%s colorspace sRGB' % lines[idx]
        #if self._extension == '.exr':
        #    idx = buf['Write']['colorspace']
        #    lines[idx] = ' colorspace linear\n'
        idx = buf['Write']['file']
        lines[idx] = ' file %s\n' % self._destination

        return lines

    def getCodecList(self, filename):
        codec_dictionary = {}
        dataList = {}
        fp = __builtin__.open(filename)
        lines = fp.readlines()
        for line in lines:
            if line.find('[') != -1:
                dataList = {}
                codecName = line[1:-2].strip()
                isCodec = 1
            else:
                isCodec = 0
            if not line.find('settings') != -1:
                fps = line.strip()
            else:
                if not isCodec:
                    settings = line # or line.rstrip()
                    dataList[fps] = settings
                    codec_dictionary[codecName] = dataList
        return codec_dictionary

def open(f):
    return Nuke(f)


if __name__ == '__main__':
    import sys
    nk = open('template/master.nk')
    #nk = open('/show/wuxia/seq/AA/AA01/roto/dev/scenes/AA01_roto_01_01.nk')
    print nk.script_test()
    sys.exit()
    # if slate
    nk.set_source('/Users/higgsdecay/output/source/0813.%05d.dpx') # change path
    nk.set_codec('Photo-JPEG')
    nk.set_fps('23.98')
    nk.set_slate(True)
    nk.set_format('1920', '1080', '1', 'Default 1920x1080')
    nk.set_note(True, 'no comment')
    nk.set_username(True, 'no comment')
    nk.set_date(True, 'no comment')
    nk.set_projectname(True, 'no comment')
    nk.set_frame(True, 'no comment')
    nk.set_lut(True, '/users/higs')
    #nk.set_letterbox(True, '873')
    nk.set_opacity('1')
    nk.set_frame_range('1-100')
    nk.set_destination('/local/test.mov')
    print nk.script()


