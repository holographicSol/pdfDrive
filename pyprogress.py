""" PyProgress - Written By Benjamin Jack Cullen """

import colorama

colorama.init()

i_char_progress = 0

spin_a = ['  |  ', '  /  ', '  -  ']

spin_b = ['  |  ', '  \\  ', '  -  ']

period_a = ['.   ', '..  ', '... ', '....']

period_b = ['   .   ', '  ...  ', ' ..... ', '.......']

period_c = ['   .   ', '  ...  ', ' ..... ', '.......',
            '.     .', '..   ..', '... ...', '.......']

period_d = ['   _   ', '  ___  ', ' _____ ', '_______',
            '_     _', '__   __', '___ ___', '_______']

arrow_a = ['       ', '>      ', '>>     ', '>>>    ', '>>>>   ', '>>>>>  ', '>>>>>> ', '>>>>>>>']

arrow_b = ['       ', '      <', '     <<', '    <<<', '   <<<<', '  <<<<<', ' <<<<<<', '<<<<<<<']

factor_100 = [1, 2, 4, 5, 10, 20, 25, 50, 100]

color_ = {'BLACK': colorama.Fore.BLACK,
          'RED': colorama.Fore.RED,
          'GREEN': colorama.Fore.GREEN,
          'YELLOW': colorama.Fore.YELLOW,
          'BLUE': colorama.Fore.BLUE,
          'MAGENTA': colorama.Fore.MAGENTA,
          'CYAN': colorama.Fore.CYAN,
          'WHITE': colorama.Fore.WHITE,
          'LIGHTBLACK_EX': colorama.Fore.LIGHTBLACK_EX,
          'LIGHTRED_EX': colorama.Fore.LIGHTRED_EX,
          'LIGHTGREEN_EX': colorama.Fore.LIGHTGREEN_EX,
          'LIGHTYELLOW_EX': colorama.Fore.LIGHTYELLOW_EX,
          'LIGHTBLUE_EX': colorama.Fore.LIGHTBLUE_EX,
          'LIGHTMAGENTA_EX': colorama.Fore.LIGHTMAGENTA_EX,
          'LIGHTCYAN_EX': colorama.Fore.LIGHTCYAN_EX,
          'LIGHTWHITE_EX': colorama.Fore.LIGHTWHITE_EX
          }

bg_color_ = {'BLACK': colorama.Back.BLACK,
          'RED': colorama.Back.RED,
          'GREEN': colorama.Back.GREEN,
          'YELLOW': colorama.Back.YELLOW,
          'BLUE': colorama.Back.BLUE,
          'MAGENTA': colorama.Back.MAGENTA,
          'CYAN': colorama.Back.CYAN,
          'WHITE': colorama.Back.WHITE,
          'LIGHTBLACK_EX': colorama.Back.LIGHTBLACK_EX,
          'LIGHTRED_EX': colorama.Back.LIGHTRED_EX,
          'LIGHTGREEN_EX': colorama.Back.LIGHTGREEN_EX,
          'LIGHTYELLOW_EX': colorama.Back.LIGHTYELLOW_EX,
          'LIGHTBLUE_EX': colorama.Back.LIGHTBLUE_EX,
          'LIGHTMAGENTA_EX': colorama.Back.LIGHTMAGENTA_EX,
          'LIGHTCYAN_EX': colorama.Back.LIGHTCYAN_EX,
          'LIGHTWHITE_EX': colorama.Back.LIGHTWHITE_EX
          }


def check_factor(factor):
    """ check if specified factor is a factor of 100 """

    allow_bool = False
    if factor in factor_100:
        allow_bool = True
    return allow_bool


def multiplier_from_inverse_factor(factor):
    """ create a multiplier from factor's inverse factor in the list of factors """

    """ invert list of factors """
    inverse_factor_100 = factor_100[::-1]

    """ iterate and match an apposing factor in the list to factor specified """
    i = 0
    for _ in factor_100:
        if _ == factor:
            multiplier = inverse_factor_100[i]
        i += 1
    return multiplier


def clear_console_line(char_limit):
    """ clear n chars from console """

    print(' '*char_limit, end='\r', flush=True)


def pr_technical_data(technical_data=''):
    """ clears console line and then prints """

    print(technical_data, end='\r', flush=True)


def progress_bar(n_progress_bar=1,
                 n_progress_space_char=' ',
                 part=int, whole=int, percent=True, color='', bg_color='', encapsulate_l_color='', encapsulate_r_color='',
                 pre_append='', append='', encapsulate_l='', encapsulate_r='', progress_char='', factor=100,
                 percent_type=int, multiplier=1,
                 part_2=int, whole_2=int, percent_2=True, color_2='', bg_color_2='', encapsulate_l_color_2='', encapsulate_r_color_2='',
                 pre_append_2='', append_2='', encapsulate_l_2='', encapsulate_r_2='', progress_char_2='', factor_2=100,
                 percent_type_2=int, multiplier_2=1):
    """
    part=int, whole=int, percent=bool,
    color=str, bg_color=str
    encapsulate_l_color=str
    encapsulate_r_color=str
    pre_append=str, append=str,
    encapsulate_l=str, encapsulate_r=str,
    progress_char=str,
    factor=int,
    multiplier=int

    Note: extremely customizable. The only required values are part=int and whole=int. Set other values as desired/necessary.

    factor_100 = [1, 2, 4, 5, 10, 20, 25, 50, 100]

    Use a factors inverse factor as a multiplier for an offset percentage independent of the progress bar.
        Example: if factor=100 then multiplier=1
        Example: factor=10 then multiplier=10 (has no opposing factor because 10 is in the middle).

        % 1: progress bar displayed
        % 2: digits displayed

    Adjust length of progress bar:
        Factor must be a factor of 100 and the same factor should be used when calling multiplier_from_inverse_factor
        as when calling multiplier_from_inverse_factor.
        1. first set the multiplier (creates a multiplier from a factors apposing factor in the list):
            multiplier = pyprogress.multiplier_from_inverse_factor(factor=factor)
        2. call this function.

    """
    pr_data = ''
    pr_data_2 = ''
    if n_progress_bar == 1 or n_progress_bar == 2:
        if check_factor(factor) is True:
            prc = int(int(factor) * float((float(part) / whole)))

            offset = float(int(factor) * float((float(part) / whole))) * multiplier
            if percent_type == int:
                offset = int(offset)

            if color and bg_color == '':
                if percent is True:
                    pr_data = colorama.Style.BRIGHT + color_[color] + str(prc * progress_char) + colorama.Style.RESET_ALL
                else:
                    pr_data = colorama.Style.BRIGHT + color_[color] + str(prc * progress_char) + colorama.Style.RESET_ALL

            elif color and bg_color:
                if percent is True:
                    pr_data = bg_color_[bg_color] + color_[color] + str(prc * progress_char) + colorama.Style.RESET_ALL
                else:
                    pr_data = bg_color_[bg_color] + color_[color] + str(prc * progress_char) + colorama.Style.RESET_ALL

            elif bg_color and color == '':
                if percent is True:
                    pr_data = bg_color_[bg_color] + str(prc * progress_char) + colorama.Style.RESET_ALL
                else:
                    pr_data = bg_color_[bg_color] + str(prc * progress_char) + colorama.Style.RESET_ALL

            else:
                if percent is True:
                    pr_data = str(prc * progress_char)
                else:
                    pr_data = str(prc * progress_char)

            if encapsulate_l and encapsulate_r:
                if encapsulate_l_color and encapsulate_r_color:
                    pr_data = color_[encapsulate_l_color] + encapsulate_l + colorama.Style.RESET_ALL + pr_data + str(' ' * int(int(factor) - prc)) + color_[encapsulate_r_color] + encapsulate_r + colorama.Style.RESET_ALL
                else:
                    pr_data = encapsulate_l + pr_data + str(' ' * int(int(factor)-prc)) + encapsulate_r
            if percent is True:
                pr_data = str(offset) + '% ' + pr_data

            if pre_append:
                pr_data = pre_append + pr_data
            if append:
                pr_data = pr_data + append

    if n_progress_bar == 2:
        if check_factor(factor_2) is True:
            prc_2 = int(int(factor_2) * float((float(part_2) / whole_2)))

            offset_2 = float(int(factor_2) * float((float(part_2) / whole_2))) * multiplier_2
            if percent_type_2 == int:
                offset_2 = int(offset_2)

            if color_2 and bg_color_2 == '':
                if percent_2 is True:
                    pr_data_2 = colorama.Style.BRIGHT + color_[color_2] + str(
                        prc_2 * progress_char_2) + colorama.Style.RESET_ALL
                else:
                    pr_data_2 = colorama.Style.BRIGHT + color_[color_2] + str(
                        prc_2 * progress_char_2) + colorama.Style.RESET_ALL

            elif color_2 and bg_color_2:
                if percent_2 is True:
                    pr_data_2 = bg_color_[bg_color_2] + colorama.Style.BRIGHT + color_[color_2] + str(
                        prc_2 * progress_char_2) + colorama.Style.RESET_ALL
                else:
                    pr_data_2 = bg_color_[bg_color_2] + colorama.Style.BRIGHT + color_[color_2] + str(
                        prc_2 * progress_char_2) + colorama.Style.RESET_ALL

            elif bg_color_2 and color_2 == '':
                if percent_2 is True:
                    pr_data_2 = bg_color_[bg_color_2] + str(prc_2 * progress_char_2) + colorama.Style.RESET_ALL
                else:
                    pr_data_2 = bg_color_[bg_color_2] + str(prc_2 * progress_char_2) + colorama.Style.RESET_ALL

            else:
                if percent_2 is True:
                    pr_data_2 = str(prc_2 * progress_char_2)
                else:
                    pr_data_2 = str(prc_2 * progress_char_2)

            if encapsulate_l_2 and encapsulate_r_2:
                if encapsulate_l_color_2 and encapsulate_r_color_2:
                    pr_data_2 = color_[
                                  encapsulate_l_color_2] + encapsulate_l_2 + colorama.Style.RESET_ALL + pr_data_2 + str(
                        ' ' * int(int(factor_2) - prc_2)) + color_[
                                  encapsulate_r_color_2] + encapsulate_r_2 + colorama.Style.RESET_ALL
                else:
                    pr_data_2 = encapsulate_l_2 + pr_data_2 + str(' ' * int(int(factor_2) - prc_2)) + encapsulate_r_2
            if percent_2 is True:
                pr_data_2 = str(offset_2) + '% ' + pr_data_2

            if pre_append_2:
                pr_data_2 = pre_append_2 + pr_data_2
            if append_2:
                pr_data_2 = pr_data_2 + append_2

    if n_progress_bar == 1:
        if append:
            clear_console_line(char_limit=int(len(pr_data)))
        pr_technical_data(technical_data=pr_data)
    elif n_progress_bar == 2:
        if append_2:
            clear_console_line(char_limit=int(len(pr_data)) + int(len(n_progress_space_char)) + int(len(pr_data_2)))
        pr_technical_data(technical_data=str(pr_data + n_progress_space_char + pr_data_2))


def display_progress_unknown(str_progress='', progress_list=[], color='', str_pre_append='', str_append=''):
    """ A simple function to display progress when overall progress is unknown. Useful when a 'whole' is unknown. """

    global i_char_progress
    print(str_progress + str_pre_append + color_[color] + progress_list[i_char_progress] + colorama.Style.RESET_ALL + str_append, end='\r', flush=True)
    if i_char_progress == int(len(progress_list))-1:
        i_char_progress = 0
    else:
        i_char_progress += 1


def display_color_options():
    return color_.keys()
