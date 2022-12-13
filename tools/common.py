import re
import json
import datetime
from pathlib import Path
from typing import Union

from dateutil.relativedelta import relativedelta


def multi(v):
    "Return a list whether property is multiple, single, or null."
    if isinstance(v, (dict, str)):
        return [v]
    if v is None:
        return []
    return v



class Location:
    def __init__(self, data=None):
        self.text = None
        self.iso2: Union[str, None] = None
        self.lat: Union[float, None] = None
        self.lon: Union[float, None] = None

        if data:
            if isinstance(data, str):
                self.iso2 = data
            else:
                self.iso2 = data.get("iso2", None)
                self.lat = data.get("lat", None)
                self.lon = data.get("lon", None)



class Social:
    def __init__(self, data=None):
        self.platform: Union[str, None] = None
        self.handle: Union[str, None] = None
        self.url: Union[str, None] = None

        if data:
            self.platform = data.get("platform", None)
        if data:
            self.handle = data.get("handle", None)
        if data:
            self.url = data.get("url", None)



class LocationMixin:
    def __init__(self, data):
        self.alias = []
        self.location = []
        self.website = []
        self.social = []

    def load(self, data: Union[dict, str, Path]):
        self.alias += multi(data.get("alias", None))
        self.location += [Location(v) for v in multi(data.get("address", None))]
        self.location += [Location(v) for v in multi(data.get("country", None))]
        self.website += multi(data.get("website", None))
        self.social += [Social(v) for v in multi(data.get("social", None))]



class Organiser(LocationMixin):
    def __init__(self, data=None):
        self.name = None

        super().__init__(data)

        if data:
            self.load(data)


    def load(self, data: Union[dict, str, Path]):
        self.name = data["name"]

        super().load(data)



class Exhibitor(LocationMixin):
    def __init__(self, data=None):
        self.name = None
        self.exhibitorUrl = None
        self.category = []

        super().__init__(data)

        if data:
            self.load(data)


    def load(self, data: Union[dict, str, Path]):
        self.name = data["name"]
        self.exhibitorUrl = data.get("exhibitorUrl", None)
        self.category += multi(data.get("category", None))

        super().load(data)



class Delegation():
    def __init__(self, data=None):
        self.name = None
        self.attended: Union[bool, None] = None
        self.retracted: Union[bool, None] = None

        if data:
            self.load(data)


    def load(self, data: Union[dict, str, Path]):
        self.name = data["name"]
        self.attended = data.get("attended", None)
        self.retracted = data.get("retracted", None)



class Fair(LocationMixin):
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, data=None):
        self.name = None
        self.start_date: Union[datetime.date, None] = None
        self.end_date: Union[datetime.date, None] = None
        self.approx_date: Union[datetime.date, None] = None
        self.series: Union[str, None] = None
        self.edition: Union[str, None] = None
        self.online: Union[bool, None] = None
        self.organiser = []
        self.exhibitor = []
        self.exhibitor_list_url = []
        self.exhibitorListDate: Union[datetime.datetime, None] = None
        self.delegation = []
        self.delegation_list_url = []
        self.delegationListDate: Union[datetime.datetime, None] = None

        super().__init__(data)

        if data:
            self.load(data)


    def load(self, data: Union[dict, str, Path]):
        self.slug = None

        if isinstance(data, str):
            data = Path(data)
        if isinstance(data, Path):
            self.slug = re.sub(r"\.json$", "", data.name)
            data = json.loads(data.read_text())

        self.name = data["name"]
        if approx_date_str := data.get("approxDate", None):
            approx_date_str = (approx_date_str + "-01-01")[:10]
            self.approx_date = approx_date_str
            self.start_date = datetime.datetime.strptime(approx_date_str, Fair.DATE_FORMAT).date()
            self.end_date = self.start_date + relativedelta(years=1, days=-1)
        else:
            self.start_date = datetime.datetime.strptime(data["startDate"], Fair.DATE_FORMAT).date()
            self.end_date = datetime.datetime.strptime(data["endDate"], Fair.DATE_FORMAT).date()
        self.series = data.get("series", None)
        self.edition = data.get("edition", None)
        self.online = data.get("online", None)

        organiser_list = multi(data.get("organiser", None))
        if organiser_list:
            self.organiser = [Organiser(v) for v in organiser_list]

        self.exhibitor_list_url = multi(data.get("exhibitorListUrl", None))
        date = data.get("exhibitorListDate", None)
        if date:
            self.exhibitor_list_date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S+00:00")
        exhibitor_list = data.get("exhibitor", None)
        if exhibitor_list:
            self.exhibitor = [Exhibitor(v) for v in exhibitor_list]

        self.delegation_list_url = multi(data.get("delegationListUrl", None))
        date = data.get("delegationListDate", None)
        if date:
            self.delegation_list_date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S+00:00")
        delegation_list = data.get("delegation", None)
        if delegation_list:
            self.delegation = [Delegation(v) for v in delegation_list]

        super().load(data)


    def iter_exhibitor(self):
        yield from self.exhibitor




def iter_fair(path: Path):
    if isinstance(path, str):
        path = Path(path)
    for fair_path in path.glob("*.json"):
        yield Fair(fair_path)



def iter_exhibitor(path: Path, multiple: Union[bool, None] = None):
    for fair in iter_fair(path):
        for exhibitor in fair.iter_exhibitor():
            yield fair, exhibitor



def iter_exhibitor_location(path: Path, multiple: Union[bool, None] = None):
    for fair, exhibitor in iter_exhibitor(path):
        if not exhibitor.location:
            continue
        if multiple:
            for location in exhibitor.location:
                yield fair, exhibitor, location
        else:
            for location in exhibitor.location[:1]:
                yield fair, exhibitor, location
