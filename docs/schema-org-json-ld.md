# Schema.org and JSON-LD

Some notes about the structure of the arms fair JSON files as they relate to Schema.org and JSON-LD.


## Source URLs

The following are all aliased to [URL](https://schema.org/URL):

-   `website`: The event or organization's official website.
-   `exhibitorListUrl`: An official page that provided the list of exhibition exhibitors.
-   `exhibitorUrl`: A page of the exhibition website for a specific exhibitor.
-   `organizerUrl`: A page of the exhibition website that specifies the organizer.


## Status, Attendance Mode

See: [EventStatusType](https://schema.org/EventStatusType), [EventAttendanceModeEnumeration](https://schema.org/EventAttendanceModeEnumeration).


## Exhibitors

[Performer](https://schema.org/performer) is the Schema.org type that best approximates an exhibitor, since they both come to present to attendees. Here we have used `exhibitor` as an alias to `performer` to reduce ambiguity.


## Social Media

Schema.org does not have a type for social media handles, so no effert has been made to standardise these..


## Exhibition Series

The [EventSeries](https://schema.org/EventSeries) type and the [superEvent](https://schema.org/superEvent) property have been used to specify the series of events to which the exhibition belongs.


## Tags

Many exhibitions use a system of tags to categorize exhibitors. Usualy these describe the kinds products and services that exhibitors offer. We have not used Schema.org types for these categories for two reasons:

-   They may also be used to indicate other types for information such as sponsorship level or stall location.
-   They are general and imprecise categories of products or services and thus not specific representable as nodes.

Further, since `category` is already used as a property name by Schema.org, we have opted to use the key `tag`.
