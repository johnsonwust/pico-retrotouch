# SPDX-License-Identifier: MIT
"""Original sample story for a tiny HyperCard-style card viewer."""
CARDS = [
    {'title': 'The Missing Floppy', 'art': 'room',
     'body': ['It is 1984. Your first picture', 'is on a missing floppy disk.', 'Search the room. Tap the artwork!'],
     'buttons': [['Desk', 1], ['Library', 2], ['Studio', 3]]},
    {'title': 'A Secret Drawer', 'art': 'desk',
     'body': ['The little drawer is locked.', 'A brass key might fit.', 'Tap the drawer after finding it.'],
     'buttons': [['Library', 2], ['Home', 0], ['Window', 4]]},
    {'title': 'The Library', 'art': 'books',
     'body': ['Old manuals line the shelf.', 'Something tiny glints below them.', 'Could that be the missing key?'],
     'buttons': [['Desk', 1], ['Home', 0], ['Studio', 3]]},
    {'title': 'The Pixel Studio', 'art': 'studio',
     'body': ['Make a memory in black and white.', 'Paint and save your own picture.', 'Your gallery lives on the SD card.'],
     'buttons': [['Paint', 'app:Paint'], ['Home', 0], ['Gallery', 'app:Gallery']]},
    {'title': 'A Window in Time', 'art': 'window',
     'body': ['A small screen. A big new world.', 'Clicking pictures feels like magic.', 'The stars are waiting outside.'],
     'buttons': [['Desk', 1], ['Home', 0], ['Library', 2]]},
    {'title': 'You Found It!', 'art': 'floppy',
     'body': ['The floppy is safe. Well done!', 'Make a new picture of your own.', 'Every little screen has a story.'],
     'buttons': [['Paint', 'app:Paint'], ['Home', 0], ['Gallery', 'app:Gallery']]}
]
