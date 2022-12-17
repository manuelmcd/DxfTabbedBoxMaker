# SPDX-FileCopyrightText: 2022-present Manuel Desbonnet <manueld@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
import sys

if __name__ == '__main__':
    from .cli import dxftabbedboxmaker

    sys.exit(dxftabbedboxmaker())
