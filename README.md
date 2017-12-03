![POLITICO](https://rawgithub.com/The-Politico/src/master/images/logo/badge.png)

# django-crosswalk

TK.


### Design notes


#### Entity domains

Definitions:
- Each entity belongs to a domain.
- Domains represent thematic divided blocks of entities that help to minimize the block we attempt to match in.
- Domains can be nested.

Examples:
- States, counties, politicians, political donors, people, company

### entity

Belongs to a domain, has a uuid and a set of attributes
May be an alias for another record.

#### Matching

Users should always specify a domain.

Can specify to include entities in child domains, default is false.

User submits an attribute map to match on.

Can specify a list of attributes to match exactly.

- Best match (with fuzzywuzzy process)
