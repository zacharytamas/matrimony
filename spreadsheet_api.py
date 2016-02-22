import json
import gspread
import logging
from oauth2client.client import SignedJwtAssertionCredentials

# credentials.json file from Google Cloud Console.
# See: http://gspread.readthedocs.org/en/latest/oauth2.html
CONFIG = json.load(open('credentials.json'))
scope = ['https://spreadsheets.google.com/feeds']

credentials = SignedJwtAssertionCredentials(CONFIG['client_email'], CONFIG['private_key'].encode(), scope)

DATA_WORKSHEET_NAME = "Data"
COL_INFO_NAME_PRIMARY = 1

COL_NAMES = [
  "primaryName",
  "mailingName",
  "secondaryNames",
  "expectedHeadCount",
  "brideOrGroom",
  "category",
  "addressStreet",
  "addressCity",
  "addressState",
  "addressZipCode",
  "sdEnvelopePrinted",
  "-",
  "rsvpCode",
  "rsvpResponseMethod",
  "rsvpAttending",
  "rsvpHeadcount",
  "rsvpMealPreference",
]

COL_INDEXES = {}
COL_LETTERS = {}

# NOTE This just dynamically generates all the column indexes with their
# names from above. This is easier in case I need to change the schema of
# my spreadsheet later: I can just enter the new column in the list above
# in its appropriate place and not have to worry about recalculating all
# the indexes.
def magicIndexes():
  count = 1
  for name in COL_NAMES:
    COL_INDEXES[name] = count
    # This little hack will work as long as we stay under 26 columns
    COL_LETTERS[name] = chr((count - 1) + ord("A"))
    count += 1
magicIndexes()

SHARED_SERVICE = gspread.authorize(credentials)


class SpreadsheetService(object):

  spreadsheet_id = CONFIG['spreadsheet_id']  # For privacy.

  service = None
  spreadsheet = None
  worksheet = None

  def __init__(self):
    self.service = SHARED_SERVICE
    self.__getSpreadsheet()

  def __getSpreadsheet(self):
    if self.spreadsheet is None or self.worksheet is None:
      self.spreadsheet = self.service.open_by_key(self.spreadsheet_id)
      self.worksheet = self.spreadsheet.worksheet(DATA_WORKSHEET_NAME)

  def __findRowForCode(self, code):
    """Finds the row of the spreadsheet which corresponds to a
    given RSVP code."""

    # TODO This O(n) search is pretty time-consuming. Depending on what I end
    # up using for the invite codes, I may can come up with a heuristic which
    # will let me find the row number in O(1) time. To do that though will
    # make the code more brittle because then we can't resort the invite
    # list in the spreadsheet without breaking the website. This may not be
    # a problem though if we just, for example, said "No sorting". There's
    # only a handful of us using the spreadsheet anyway so it may be okay
    # to just make that rule.

    try:
      return self.worksheet.col_values(COL_INDEXES["rsvpCode"]).index(code) + 1
    except ValueError:
      return

  def __writeValue(self, row_number, col_name, value):
    """Convenience method for writing a value to the spreadsheet."""
    self.worksheet.update_cell(row_number, COL_INDEXES[col_name], value)

  def __getValueFromRow(self, row, col_name):
    """Just a convenience accessor to get values from
    certain columns of a row."""
    return row[COL_INDEXES[col_name] - 1]

  def guestLookup(self, code):
    """Returns information about a guest based on their invite code."""
    row_number = self.__findRowForCode(code)
    row = self.worksheet.row_values(row_number)

    return {
      "primaryName": self.__getValueFromRow(row, "primaryName")
    }

  def RSVP(self, code, attending, headcount, meal_preference):
    row_number = self.__findRowForCode(code)

    if not row_number:
      raise ValueError("RSVP not found")

    rsvp_range = "%s%d:%s%d" % (COL_LETTERS["rsvpResponseMethod"], row_number,
                                COL_LETTERS["rsvpMealPreference"], row_number)

    # This quirky method allows us to update them in a batch.
    selection = self.worksheet.range(rsvp_range)
    values = ["Online", "YES" if attending else "NO", headcount, meal_preference]

    for cell, value in zip(selection, values):
      cell.value = value

    self.worksheet.update_cells(selection)
