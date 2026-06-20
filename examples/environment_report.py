"""Print a non-content environment report for issue triage."""

from pprint import pprint

from plugins.environment_report_plugin import environment_report


pprint(environment_report())
