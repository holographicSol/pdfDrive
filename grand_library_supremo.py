""" Written by Benjamin Jack Cullen for my library projects """

import colorama
colorama.init()


def color(s, c):
    if c == 'W':
        return colorama.Style.BRIGHT + colorama.Fore.WHITE + str(s) + colorama.Style.RESET_ALL
    elif c == 'LM':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTMAGENTA_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'M':
        return colorama.Style.BRIGHT + colorama.Fore.MAGENTA + str(s) + colorama.Style.RESET_ALL
    elif c == 'LC':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'B':
        return colorama.Style.BRIGHT + colorama.Fore.BLUE + str(s) + colorama.Style.RESET_ALL
    elif c == 'LG':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTGREEN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'G':
        return colorama.Style.BRIGHT + colorama.Fore.GREEN + str(s) + colorama.Style.RESET_ALL
    elif c == 'Y':
        return colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(s) + colorama.Style.RESET_ALL
    elif c == 'R':
        return colorama.Style.BRIGHT + colorama.Fore.RED + str(s) + colorama.Style.RESET_ALL


supremo = color('/o\\', c='Y')
library_name = color('[Grand Library]', c='Y')


def display_grand_library():
    print('')
    print('')
    print(f'               {supremo}')
    print('      ' + '_'*21)
    print('      || ||           || ||')
    print('  ' + '_'*29)
    print(f'   || || {library_name} || ||')
    print('  ' + '_'*29)
    print(' ' + '_'*31)
    # print('    in nomine intelligentiae  ')
    # print(' ' + '_'*31)
    print('')
    print('')

