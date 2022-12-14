from abc import ABC, abstractmethod
from os.path import exists
import os
from datetime import datetime
import json

__author__ = "Christian F. (known as Chryfi)"
__copyright__ = "Copyright 2022, LectorLips"
__credits__ = ["Christian F. (known as Chryfi)", "Florian Torgau"]
__maintainer__ = "Christian F. (known as Chryfi)"
__status__ = "Production"
__version__ = "1.1"


class InvalidCommand(Exception):
    pass


class CommandException(Exception):
    pass


class InvalidCommandArguments(Exception):
    pass


class Command(ABC):
    standardParams = {"help" : "-help", "debug" : "-debug"}

    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def parse_args(self, args: list):
        pass

    @abstractmethod
    def get_documentation(self) -> str:
        pass

    # Cleanup arguments from the standard parameters that are not specific to a Command
    def clean_args(self, args: list) -> list:
        args_cleaned = args.copy()

        for key, param in self.standardParams.items():
            if param in args_cleaned:
                args_cleaned.remove(param)

        return args_cleaned


class HelpCommand(Command):

    def __init__(self, args):
        pass

    def execute(self) -> None:
        print("List of possible commands:")

        for command in commands.keys():
            print(command)

        print("\nList of parameters that can be used with every command:")

        for key, param in self.standardParams.items():
            print(param)

    def parse_args(self, args: list) -> bool:
        pass

    @staticmethod
    def get_documentation() -> str:
        return ""


class CreateSequencerNBT(Command):
    minRequiredArgs = 2
    maxArgs = 4
    standardEndTickDuration = 100

    def __init__(self, args: list):
        self.endTickDuration = self.standardEndTickDuration
        self.filePath = None
        self.texturePath = None
        self.visemePath = VisemeMappingFile.fileName
        self.parse_args(args)

    def execute(self) -> None:
        fps_marker = "Units Per Second"
        time_remap_marker = "Time Remap"

        fps = None
        keyframes = None

        with open(self.filePath, 'r') as file:
            while True:
                line = file.readline()

                if not line:
                    break

                line = line.strip()

                if fps_marker in line:
                    fps = float(line.replace(fps_marker, "").strip())
                elif time_remap_marker in line:
                    file.readline()  # skip marker line
                    keyframes = self.parse_keyframes(file)

                    break

        if fps is None:
            raise CommandException("The \"" + fps_marker + "\" were not found in the keyframe file!")
        if keyframes is None:
            raise CommandException("The keyframes were not found or are empty. The keyframes are usually located at \"" + time_remap_marker + "\"")

        sequencerNBT = self.convert_to_sequencer_morph(keyframes, fps)

        with open(datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + "_output.txt", 'x') as f:
            f.write(sequencerNBT)

        print("File was successfully created.")

    def convert_to_sequencer_morph(self, keyframes: list, fps: int) -> str:
        viseme_mapping = self.load_viseme_mapping()

        nbt_start = "{List:["
        nbt_end = "],KeepProgress:1b,Name:\"sequencer\",Offset:[0.0f,0.0f,0.0f]}"

        if keyframes is not None:
            for i in range(len(keyframes)):
                keyframe = keyframes[i]
                frame = float(keyframe[0])
                mouth = int(keyframe[1])

                if mouth >= len(viseme_mapping):
                    print("Skipped frame " + str(frame) + " with mouth " + str(mouth) + ". Mouth out of viseme mapping range!")
                    continue

                if i < len(keyframes) - 1:
                    next_keyframe = keyframes[i + 1]
                    next_frame = float(next_keyframe[0])
                    tick_duration = (next_frame - frame) / fps * 20
                else:
                    tick_duration = self.endTickDuration

                morph_nbt = "Morph: { Texture:\"" + self.texturePath + viseme_mapping.get(str(mouth)) + "\", Name:\"blockbuster.image\"}"

                nbt_start += "{Random:0.0f, SetDuration:1b, " + morph_nbt + ", Duration:" + str(tick_duration) + "f, EndPoint:0b}" + ("," if i < len(keyframes) - 1 else "")

        return nbt_start + nbt_end

    def load_viseme_mapping(self) -> dict:
        mapping = VisemeMappingFile.read(self.visemePath)

        if mapping is None:
            raise CommandException("The viseme mapping configuration file does not exist yet. You have to create the file using the command or do it manually.")
        elif len(mapping) == 0:
            raise CommandException("Something went wrong during reading the viseme mapping file! The mapping is empty.")

        return mapping

    def parse_keyframes(self, file) -> list:
        keyframes = []

        while True:
            line = file.readline().strip()

            if not line:
                break

            keyframe = line.split()

            keyframes.append(keyframe)

        return keyframes

    def parse_args(self, args: list):
        if self.standardParams.get("help") in args:
            print(self.get_documentation())

            quit(0)

        args_cleaned = self.clean_args(args)

        if len(args_cleaned) < self.minRequiredArgs:
            raise InvalidCommandArguments("Not all required arguments were provided")

        if len(args_cleaned) > self.maxArgs:
            raise InvalidCommandArguments("Unknown arguments: " + "".join(("\"" + str(args_cleaned[i]) + "\"" + (", " if i < len(args_cleaned) - 1 else "")) for i in range(len(args_cleaned))))

        self.check_file_path(args_cleaned[0])

        self.filePath = args_cleaned[0]
        self.texturePath = self.check_texture_path(args_cleaned[1])

        if len(args_cleaned) > 2:
            if not args_cleaned[2].isnumeric():
                raise InvalidCommandArguments("Third argument should be a number!")
            else:
                self.endTickDuration = args_cleaned[2]

        if len(args_cleaned) > 3:
            self.visemePath = args_cleaned[3]

    @staticmethod
    def get_documentation() -> str:
        return "Command arguments:\n<file path>  <image morph texture path>  optional: <end tick duration> <viseme_mapping_filename>\n\n" \
               "Documentation:\n<file path> the global or relative file path to the keyframes data\n" \
               "<image morph texture path> the Blockbuster file path to the image folder containing the mouth images for example \"b.a:skins/mouths/\"\n" \
               "Optional:\n<end tick duration> the duration of the last morph. Default is " + str(CreateSequencerNBT.standardEndTickDuration) + "\n" \
               "<viseme_mapping_filename> the name of a new viseme mapping file."

    def check_file_path(self, file_path: str):
        if not str(file_path).endswith(".txt"):
            raise CommandException("Keyframe file path does not end with a .txt! The keyframe data should be pasted into a .txt file.")

        if not exists(file_path):
            raise CommandException("Keyframe file does not exist at the specified path!")

    #return corrected file path
    def check_texture_path(self, file_path: str) -> str:
        if file_path.find(':') == -1:
            raise CommandException("Texture file path seems to be incorrect. It misses ':', for example 'blockbuster:textures/..'!")

        if not file_path.endswith("/"):
            file_path += "/"

        return file_path


class CreateVisemeMapping(Command):
    minArgs = 15
    maxArgs = 16

    def __init__(self, args: list):
        self.args = []
        self.visemeName = VisemeMappingFile.fileName
        self.parse_args(args)

    def execute(self) -> None:
        viseme_mapping = {}

        for i in range(15):
            viseme_mapping[str(i)] = self.args[i]

        VisemeMappingFile.write(viseme_mapping, self.visemeName)

        print("Successfully created json viseme mapping configuration file.")

    def parse_args(self, args: list):
        if self.standardParams.get("help") in args:
            print(self.get_documentation())

            quit(0)

        self.args = self.clean_args(args)

        if len(self.args) < self.minArgs:
            raise InvalidCommandArguments("Missing required " + str(self.minArgs) + " arguments.")

        if len(self.args) > self.maxArgs:
            raise InvalidCommandArguments("More than " + str(self.maxArgs) + " arguments were given.")

        if len(self.args) > 15:
            if not self.args[15].endswith(".json"):
                raise InvalidCommandArguments("The viseme mapping filename does not end with .json!")
            else:
                self.visemeName = self.args[15]


    @staticmethod
    def get_documentation() -> str:
        return "Command arguments:\n<list of 15 image file names>  optional: <viseme_mapping_filename>\n\n"\
               "<list of 15 image file names> type in 15 image file names in ascending order matching the viseme mapping.\n" \
               "Optional:\n<viseme_mapping_filename> if you want multiple viseme mapping files, you can specify your " \
               "own filename. The filename should end with .json"


class VisemeMappingFile:
    fileName = "viseme_mapping.json"
    @staticmethod
    def write(mapping: list):
        VisemeMappingFile.write(mapping, VisemeMappingFile.fileName)

    @staticmethod
    def write(mapping: list, file_name: str):
        if exists(file_name):
            os.remove(file_name)

        with open(file_name, 'x') as file:
            file.write(json.dumps(mapping, indent=4))

    @staticmethod
    def read():
        VisemeMappingFile.read(VisemeMappingFile.fileName)

    @staticmethod
    def read(file_name: str) -> list:
        if not exists(file_name):
            return None

        with open(file_name, 'r') as file:
            return json.loads(file.read())

commands = {"-help": globals()["HelpCommand"], "-create_sequencer": globals()["CreateSequencerNBT"], "-create_viseme_mapping": globals()["CreateVisemeMapping"]}
