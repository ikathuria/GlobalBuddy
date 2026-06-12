---
id: task_apply_ssn
type: Task
title: Apply for SSN if eligible
city: Chicago
category: document
when: first_week
priority: medium
estimated_day_window: Day 7-14
needs:
  - documents
  - employment
depends_on:
  - task_retrieve_i94
  - task_open_bank_account
description: Apply only when eligible, usually with on-campus employment or another qualifying reason.
links_to:
  - localentity_chicago_social_security_office
---

# Apply for SSN if eligible

Verify eligibility with your international office before visiting the [[Chicago Social Security Office]].
