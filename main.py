import argparse
import json
import os
from sys import exit
from termcolor import colored, cprint

class Save:
    # Initialize save class
    def __init__(self, filename):
        # Open save file
        with open(filename, 'r') as f:
            data = json.load(f)['properties']['worldSaveData']['value']
        
        # Save pertinent data
        self.groups_data = data['GroupSaveDataMap']['value']
        self.bases_data = data['BaseCampSaveData']['value']
        self.slots_data = data['CharacterContainerSaveData']['value']
        self.chars_data = data['CharacterSaveParameterMap']['value']

        # Initialize guild data
        self.guilds = {}
    
    # Add guild to save
    def add_guild(self, guild_name):
        if guild_name is None:
            for idx, group in enumerate(self.groups_data):
                if group['value']['GroupType']['value']['value'] == 'EPalGroupType::Guild':
                    self.guilds[group['value']['RawData']['value']['guild_name']] = Guild(idx, self.groups_data, self.bases_data, self.slots_data, self.chars_data)
                    break
        else:
            for idx, group in enumerate(self.groups_data):
                if group['value']['RawData']['value']['guild_name'] == guild_name:
                    self.guilds[guild_name] = Guild(idx, self.groups_data, self.bases_data, self.slots_data, self.chars_data)
                    break
    
    # Write guild data to console
    def write_console(self):
        for i, (name, guild) in enumerate(self.guilds.items()):
            self.guilds[name].print_guild()
    
    # Write guild data to json file
    def write_json(self, filename):
        with open(filename, 'w') as f:
            out = [{**guild.__dict__, 'bases': [{**base.__dict__, 'pals': [pal.__dict__ for pal in base.pals]} for base in guild.bases]} for name, guild in self.guilds.items()]
            
            json.dump(out, f, indent=4)

class Guild:
    # Initialize guild class
    def __init__(self, group_idx, groups_data, bases_data, slots_data, chars_data):
        # Save guild info
        self.id = groups_data[group_idx]['key']
        self.name = groups_data[group_idx]['value']['RawData']['value']['guild_name']

        # Get guild players
        self.player_map = {player['player_uid']: player['player_info']['player_name'] for player in groups_data[group_idx]['value']['RawData']['value']['players']}

        # Get guild bases
        self.bases = []
        for idx, base in enumerate(bases_data):
            if base['key'] in groups_data[group_idx]['value']['RawData']['value']['base_ids']:
                self.bases.append(Base(idx, bases_data, slots_data, chars_data))
    
    # Print guild data
    def print_guild(self):
        if len(self.bases) == 0:
            return
        cprint(f'{self.name}', 'magenta', attrs=['bold'])
        for idx, base in enumerate(self.bases):
            if len(base.pals) == 0:
                continue
            cprint(f'  Base {idx + 1} ({base.coords[0]}, {base.coords[1]})', 'green', attrs=['bold'])
            for player in self.player_map.keys():
                if len([pal for pal in base.pals if pal.owner == player]) == 0:
                    continue
                cprint(f'    {self.player_map[player]}', 'yellow', attrs=['bold'])
                for pal in [pal for pal in base.pals if pal.owner == player]:
                    text = colored(f'      {pal.name}{'*' if pal.multiple_owners else ''} [Lvl {pal.level} / HP {pal.hp}] ', 'white')
                    if pal.nickname is not None:
                        text += colored(f'({pal.nickname}) ', 'dark_grey')
                    if pal.gender == 'Male':
                        text += colored('♂ ', 'blue')
                    elif pal.gender == 'Female':
                        text += colored('♀ ', 'magenta')
                    if pal.lucky:
                        text += colored('♦', 'cyan')
                    if pal.boss:
                        text += colored('🕱', 'red')
                    
                    print(text)

class Base:
    def __init__(self, base_idx, bases_data, slots_data, chars_data):
        # Temporarily save base data
        base_data = bases_data[base_idx]

        # Save base info
        self.id = base_data['key']
        self.container_id = base_data['value']['WorkerDirector']['value']['RawData']['value']['container_id']
        self.coords = [round(base_data['value']['WorkerDirector']['value']['RawData']['value']['spawn_transform']['translation']['y']*0.0022 - 345),
                       round(base_data['value']['WorkerDirector']['value']['RawData']['value']['spawn_transform']['translation']['x']*0.0022 + 271)]
        
        # Get slot index
        slot_idx = next(idx for idx, slot in enumerate(slots_data) if slot['key']['ID']['value'] == self.container_id)

        # Get base pals
        self.pals = [Pal(idx, chars_data) for idx, pal in enumerate(chars_data) if pal['key']['InstanceId']['value'] in [pal['RawData']['value']['instance_id'] for pal in slots_data[slot_idx]['value']['Slots']['value']['values']]]

class Pal:
    def __init__(self, char_idx, chars_data):
        # Temporary save pal data
        pal_data = chars_data[char_idx]

        # Save pal info
        self.id = pal_data['key']['InstanceId']['value']
        self.code = pal_data['value']['RawData']['value']['object']['SaveParameter']['value']['CharacterID']['value'].replace('BOSS_', '')
        self.name = PAL_NAME_BY_CODE[self.code.lower()]
        self.gender = pal_data['value']['RawData']['value']['object']['SaveParameter']['value']['Gender']['value']['value'].split('::')[1]
        self.level = pal_data['value']['RawData']['value']['object']['SaveParameter']['value']['Level']['value']
        self.hp = round(pal_data['value']['RawData']['value']['object']['SaveParameter']['value']['MaxHP']['value']['Value']['value']/1000)
        self.nickname = pal_data['value']['RawData']['value']['object']['SaveParameter']['value'].get('NickName', {}).get('value', None)
        self.owner = pal_data['value']['RawData']['value']['object']['SaveParameter']['value']['OldOwnerPlayerUIds']['value']['values'][0]
        self.lucky = pal_data['value']['RawData']['value']['object']['SaveParameter']['value'].get('IsRarePal') is not None
        self.boss = not self.lucky and 'BOSS_' in pal_data['value']['RawData']['value']['object']['SaveParameter']['value']['CharacterID']['value']
        self.multiple_owners = len(pal_data['value']['RawData']['value']['object']['SaveParameter']['value']['OldOwnerPlayerUIds']['value']['values']) > 1

def load_pal_map():
    with open('resources/pals.json', 'r') as f:
        return {pal['CodeName'].lower(): pal['Name'] for pal in json.load(f).get('values')}

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        prog='palworld-base-pal-ownership',
        description='Retrieves player ownership of guild base pals from Palworld save file',
    )
    parser.add_argument('filename', help='input json filename (example: Level.sav.json)')
    parser.add_argument('-g', '--guild', help='guild name (default: retrieve all guilds)')
    parser.add_argument('-o', '--output', help='output json filename (default: output.json)')
    parser.add_argument('-q', '--quiet', action='store_true', help='suppress console output (default: False)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.0')
    args = parser.parse_args()
    
    # Load save file
    if not os.path.exists(args.filename):
        print(f'{args.filename} does not exist')
        exit(1)
    
    save = Save(args.filename)
    save.add_guild(args.guild)

    # Output to file
    if args.output is not None:
        save.write_json(args.output)

    # Output to console
    if not args.quiet:
        save.write_console()

if __name__ == "__main__":
    # Load pal codename map
    if not os.path.exists('resources/pals.json'):
        print('pals.json not found')
        exit(1)
    PAL_NAME_BY_CODE = load_pal_map()

    # Execute main function
    main()

    # Exit program
    exit(0)
