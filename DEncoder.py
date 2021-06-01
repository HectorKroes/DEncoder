#Importing necessary libraries
from string import ascii_letters, digits, punctuation
import pyperclip, string, random, os, gzip
import PySimpleGUI as sg

#Initializing char list and dictionary

char_list = list(ascii_letters) + list(digits) + list(punctuation) + [char for char in "\nÁÂÃÀáâãàÉÊÈéêèÍÎÌíîìÓÔÕÒóôõòÚÛÙúûùç 	"]
char_dict = {char_list[index]:index+1 for index in range(len(char_list))}

#Various definitions

sg.theme('SystemDefault')

#Defining core functions

def encode(to_encode, key=''):
	if key == '':
		key = ('-'.join(random.sample([str(x) for x in range(1,133)], len(char_list))))
		key_dict = {char_list[index]:[int(x) for x in key.split('-')][index] for index in range(len(char_list))}
	else:
		key_dict = {}; key_dict = {char:index+1 for index, char in enumerate(key)}
		key = '-'.join(str(x) for x in [key_dict[char] for char in char_list])
	cid = [key_dict.get(char) for char in [char for char in to_encode]]; index_dict = tuple(key_dict.items())
	numbers = [int(number) for number in digits[1:]]; coded_list1 = []; progress = 1
	for code in cid:
		a_index = random.choice(range(1,132)); a = index_dict[a_index][1]; b = random.choice(numbers)
		coded_list1.append((((code+a)*b) ,f"{a}{b}"))
		sg.one_line_progress_meter('DEncoder', progress, len(cid), 'key','Encoding...')
		progress += 1
	coded_list2 = [f"{tup[0]}-{tup[1]}" for tup in coded_list1]
	coded_string = '-'.join(coded_list2)
	return key, coded_string

def decode(to_decode, key):
	if key.count('-') != 131 or len(key) != 419:
		key_dict = {}; key_dict = {char:index+1 for index, char in enumerate(key)}
		key = '-'.join(str(x) for x in [key_dict[char] for char in char_list])
	key_dict = {char_list[index]:[int(x) for x in key.split('-')][index] for index in range(len(char_list))}
	parsed_code= to_decode.split('-'); coded_chars = parsed_code[::2]; abcds = parsed_code[1::2]
	parsed_abcds = [[abcd[:-1], abcd[-1:]] for abcd in abcds]; equivalences = []
	for index in range(len(coded_chars)):
		coded_char = int(coded_chars[index]); a, b = [int(number) for number in parsed_abcds[index]]
		equivalences.append(int((coded_char/b)-a))
	itemsList = key_dict.items(); decoded_chars = []; progress = 1
	for eq in equivalences:
		for item  in itemsList:
			if item[1] == eq:
				decoded_chars.append(item[0])
				sg.one_line_progress_meter('DEncoder', progress, len(equivalences), 'key','Decoding...')
				progress += 1
	decoded = ''. join(decoded_chars)
	return decoded

#Instituting some GUI functions

def ReadLayout(LayoutName):
	window = sg.Window('DEncoder', LayoutName, element_justification = 'center')
	global event, values, ProgramON, Encoding, Decoding, ShowingResults
	event, values = window.Read()
	window.close()
	if event in (None, 'Exit'):
		Encoding = False; Decoding = False; ShowingResults = False
		ProgramON = False
	if event == '-menu-':
		Encoding = False; Decoding = False; ShowingResults = False

def SaveTxtFile(values, content):
	global key, coded_string
	if values['-file_name-'] != '' and values['-file_path-'] != '':
		file_name = values['-file_name-']; file_format = values['-file_format-']

		if file_format == ".txt":
			with open(f"{values['-file_path-']}{os.sep}{file_name}.txt", "w", encoding='utf-8') as file:
				file.write(content)
				RecoverSavingData(WarnMess = f'{file_name}.txt saved successfully', file_n = file_name, file_p = values['-file_path-'], file_f = file_format)

		elif file_format == ".gz":
			byte_content = bytes(content, 'utf-8')
			with gzip.open(f"{values['-file_path-']}{os.sep}{file_name}.txt.gz", 'w+') as file:
				file.write(byte_content)
				RecoverSavingData(WarnMess = f'{file_name}.txt.gz saved successfully', file_n = file_name, file_p = values['-file_path-'], file_f = file_format)

		else:
			RecoverSavingData(WarnMess = 'Select a valid file extension')

	elif values['-file_name-'] == '' and values['-file_path-'] == '':
		RecoverSavingData(WarnMess = 'Write a file name and select a folder to save it', file_f = file_format)

	elif values['-file_name-'] != '' and values['-file_path-'] == '':
		RecoverSavingData(WarnMess = 'Select a folder to save your file', file_n = values['-file_name-'], file_f = file_format)

	elif values['-file_name-'] == '' and values['-file_path-'] != '':
		RecoverSavingData(WarnMess = 'Write a file name', file_p = values['-file_path-'], file_f = file_format)

def CheckKeyType(key):
	if key.count('-') != 131 or len(key) != 419:
		random.seed(sum([char_dict[char] for char in key])); positive_char_list = []; negative_char_list = []
		for char in key:
			if char not in positive_char_list:
				positive_char_list.append(char)
		key_first_half = ''.join(positive_char_list)
		for char in char_list:
			if char not in positive_char_list:
				negative_char_list.append(char)
		key_second_half = (''.join(random.sample(negative_char_list, len(negative_char_list))))
		key = f"{key_first_half}{key_second_half}"
		random.seed()
	return key

def CheckForKey():
	FrameLayout1 = [[sg.Multiline(ML_InitialInput, size = (52,18), key = '-specific_key-')]]
	CheckForKeyLayout = [[sg.Frame('Insert your specific key', FrameLayout1)],
		[sg.Button('Encode', size = (52, 1), key = '-encode-')]]
	ReadLayout(CheckForKeyLayout)
	return CheckKeyType(values['-specific_key-'].strip('\n'))

def CheckStringLength(string, operation):
	if len(string) > 10000:
		return f"Your {operation} string is too long to be shown here, you can still save it to a file or copy it to your clipboard."
	else:
		return string

def EncodeString(message, predefined_key):
	key, coded_string = encode(message, predefined_key)

	global ShowingResults, WarningMessage, file_name, file_path, file_format
	WarningMessage = ''; file_name = ''; file_path = ''; file_format = ".txt"
	ShowingResults = True

	while ShowingResults == True:
		FrameLayout1 = [[sg.Text('Key')],
			[sg.Multiline(key , size = (54,7))],
			[sg.Text('Coded String')],
			[sg.Multiline(CheckStringLength(coded_string, "coded"), size = (54, 7))],
			[sg.Button('Copy key to clipboard', size = (23, 1), key = '-clip_key-'), sg.Button('Copy message to clipboard', size = (23,1), key = '-clip_message-')]] 
		FrameLayout2 = [[sg.Text('Name of the file:')], 
			[sg.Input(file_name, size = (46, 1), key = '-file_name-'), sg.Combo(['.txt', '.gz'], default_value = file_format, key = '-file_format-')],
			[sg.Text('Choose folder in which to save file:')],
			[sg.Input(file_path, size = (46, 1), key = '-file_path-'), sg.FolderBrowse()],
			[sg.Button('Save file', size = (48, 1), key = '-save_file-')]]        
		EncodedLayout = [[sg.Frame('Copy', FrameLayout1)],
			[sg.Frame('Save to a file', FrameLayout2)],
			[sg.Text(WarningMessage, text_color='red')],
			[sg.Button('Back to main menu', size = (24, 1), key = '-menu-'), sg.Button('Encode something else', size = (24,1), key = '-back-')]]

		ReadLayout(EncodedLayout)

		if event == '-back-':
			ShowingResults = False
			continue

		elif event == '-clip_key-':
			pyperclip.copy(key)

		elif event == '-clip_message-':
			pyperclip.copy(coded_string)

		elif event == '-save_file-':
			SaveTxtFile(values, f"{key}-0-{coded_string}")

def DecodeString(key, message):

	decoded_string = decode(message, key)
	global ShowingResults, WarningMessage, file_name, file_path, file_format; ShowingResults = True
	file_name = ''; file_path = ''; WarningMessage = ''; file_format = '.txt'

	while ShowingResults == True:
		FrameLayout1 = [[sg.Text('Your decoded message:')],
			[sg.Multiline(CheckStringLength(decoded_string, "decoded") , size = (54,7))],
			[sg.Button('Copy to clipboard', size = (49, 1), key = '-clip_message-')]]
		FrameLayout2 = [[sg.Text('Name of the file:')], 
			[sg.Input(file_name, size = (46, 1), key = '-file_name-'), sg.Combo(['.txt', '.gz'], default_value = file_format, key = '-file_format-')],
			[sg.Text('Choose folder in which to save file:')],
			[sg.Input(file_path, size = (46, 1), key = '-file_path-'), sg.FolderBrowse()],
			[sg.Button('Save file', size = (48, 1), key = '-save_file-')]]
		DecodedLayout = [[sg.Frame('Copy', FrameLayout1)],
			[sg.Frame('Save to a file', FrameLayout2)],
			[sg.Text(WarningMessage, text_color='red')],
			[sg.Button('Back to main menu', size = (24, 1), key = '-menu-'), sg.Button('Decode something else', size = (24,1), key = '-back-')]]

		ReadLayout(DecodedLayout)

		if event == '-back-':
			ShowingResults = False
			continue

		elif event == '-clip_message-':
			pyperclip.copy(decoded_string)

		elif event == '-save_file-':
			SaveTxtFile(values, f"{decoded_string[1:-1]}")

def RecoverCodingDueToInputError(WarnMess, MLII, IEII, WarnVis):
	global WarningMessage, ML_InitialInput, IE_InitialInput, Warning_Visibility
	WarningMessage = WarnMess; ML_InitialInput = MLII;
	IE_InitialInput = IEII; Warning_Visibility = WarnVis

def RecoverSavingData(WarnMess='', file_n = '', file_p = '', file_f = ".txt"):
	global WarningMessage, file_name, file_path, file_format
	WarningMessage = WarnMess; file_name = file_n; file_path = file_p; file_format = file_f

def RecoverDecodingDueToInputError(WarnMess, key_init, mess_init, file_p, WarnVis):
	global Initial_Key, Initial_Message, WarningMessage, Warning_Visibility, Initial_FP
	WarningMessage = WarnMess; Initial_Key = key_init; Initial_Message = mess_init
	Initial_FP = file_p; Warning_Visibility = WarnVis

#Proper GUI start

ProgramON = True
while ProgramON == True:

	InitialPageLayout = [  [sg.Text('DEncoder', font = "Helvetica 20")],
			[sg.Text('')],
			[sg.Button('Encode', size = (40,1))],
			[sg.Button('Decode', size = (40,1))],
			[sg.Button('Credits', size = (40,1))],
			[sg.Button('End program', size = (40,1))],
			[sg.Text('')]]

	ReadLayout(InitialPageLayout)

	if event == 'Encode':

		Encoding = True; Warning_Visibility = False; ML_InitialInput = ''; IE_InitialInput = ''; WarningMessage = 'None'

		while Encoding == True:

			FrameLayout1 = [[sg.Multiline(ML_InitialInput, size = (52,18), key = '-message-')],
				[sg.Checkbox("Check this if you'd like to use an specific key", default=False, key='-predefined_key-')]]
			FrameLayout2 = [[sg.Input(IE_InitialInput, key = '-file_path-'), sg.FileBrowse()]]        
			EncodingPageLayout = [[sg.Frame('Insert your message directly', FrameLayout1)],
				[sg.Text('or')],
				[sg.Frame('Load a file', FrameLayout2)],
				[sg.Text(WarningMessage, text_color='red', visible = Warning_Visibility)],
				[sg.Button('Back to main menu', size = (23, 1), key = '-menu-'), sg.Button('Encode!', size = (23,1), key = '-encode-')]]

			ReadLayout(EncodingPageLayout)

			if event == '-encode-':

				predefined_key = ''

				if values['-message-'] != '\n' and values['-file_path-'] == '':

					message = values['-message-'].strip('\n')
					predefined_key = ''
					if values['-predefined_key-'] == True:
						predefined_key = CheckForKey()
					EncodeString(message, predefined_key)
					if event == '-back-':
						continue

				elif values['-message-'] == '\n' and values['-file_path-'] != '':

					with open(values['-file_path-'], 'r', encoding = 'utf-8') as file:
						message = repr(file.read().replace('\n', ''))
					EncodeString(message, predefined_key)

				elif values['-message-'] != '\n' and values['-file_path-'] != '':
					RecoverCodingDueToInputError('Fill only one of the fields', values['-message-'], values['-file_path-'], True)

				elif values['-message-'] == '\n' and values['-file_path-'] == '':
					RecoverCodingDueToInputError('Fill one of the fields first', values['-message-'], values['-file_path-'], True)

	elif event == 'Decode':

		Decoding = True; Initial_Key = ''; Initial_Message = ''; WarningMessage = 'None'; Warning_Visibility = False; Initial_FP = ''

		while Decoding == True:
			FrameLayout1 = [[sg.Text('Key')],
				[sg.Multiline(Initial_Key, size = (54,7), key = '-key-')],
				[sg.Text('Coded String')],
				[sg.Multiline(Initial_Message, size = (54, 7), key = '-message-')]] 
			FrameLayout2 = [[sg.Input(Initial_FP, size= (48,1), key = '-file_path-'), sg.FileBrowse()]]         
			EncodedLayout = [[sg.Frame('Paste key and the coded message', FrameLayout1)],
				[sg.Text('or')],
				[sg.Frame('Load a file', FrameLayout2)],
				[sg.Text(WarningMessage, text_color='red', visible = Warning_Visibility)],
				[sg.Button('Back to main menu', size = (24, 1), key = '-menu-'), sg.Button('Decode!', size = (24,1), key = '-decode-')]]
			ReadLayout(EncodedLayout)

			if event == '-decode-':
				if values['-message-'] != '\n' and values['-key-'] != '\n' and values['-file_path-'] == '':
					DecodeString(CheckKeyType(values['-key-'].strip('\n')), values['-message-'].strip('\n'))

				elif values['-message-'] == '\n' and values['-key-'] == '\n' and values['-file_path-'] != '':

					if values['-file_path-'].endswith('.txt'):
						with open(values['-file_path-'], 'r') as file:
							file_text = file.read().split('-0-')

					elif values['-file_path-'].endswith('.gz'):
						with gzip.open(values['-file_path-'], 'rb') as file:
							debyted_text = file.read().decode()
							file_text = debyted_text.split('-0-')

					DecodeString(file_text[0], file_text[1])

				elif values['-message-'] != '\n' and values['-key-'] == '\n' and values['-file_path-'] == '':
					RecoverDecodingDueToInputError("Input the key for the string you want to decode", values['-key-'], values['-message-'], values['-file_path-'], True)

				elif values['-message-'] == '\n' and values['-key-'] != '\n' and values['-file_path-'] == '':
					RecoverDecodingDueToInputError("Input the string you want to decode", values['-key-'], values['-message-'], values['-file_path-'], True)

	elif event == 'Credits':
		CreditsLayout = [[sg.Text('CREDITS', justification='center')],
			[sg.Text("DEncoder was made by Hector Kroes and it's available for\nfree download at <https://github.com/HectorKroes/DEncoder>.\nIf you find errors, problems, or have a suggestion, please\nsubmit it at the GitHub repository or send an email to\nhector.kroes@outlook.com\n\nThank you!"+'\n')],
			[sg.Button('Return to main menu', size = (30,1))]]
		ReadLayout(CreditsLayout)

	elif event == 'End program':
		ProgramON = False