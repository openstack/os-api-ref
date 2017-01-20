===========
 Releasing
===========

This documents the how and when to release ``os-api-ref``.

When to release
===============

Any time there are fixes or additions ready to go, they should be
released. Releases are cheap. If it's been more than a month and there
are changes in master, consider releasing them.

If the changes are entirely on the CSS / JS cosmetic side, things are
usually pretty safe to release as long as they have been spot checked
against a couple of projects. (The gate does the nova tree
automatically).

If new warnings are added
-------------------------

If **new** warnings have been added since the last release, care
should be taken to:

 * Alert the mailing list 2 days before the release about the new
   warning coming in (that should give them time to go non enforcing
   or fix the issue).
 * Ensure that you bump at least the Y in the version number
 (X.Y.Z). New warnings are not a Z level release.

How to release
==============

Check out ``openstack/releases``

Edit ``deliverables/_independent/os-api-ref.yaml``

Add a line with the version number desired, the git has of the commit
that should be that release.

If you have questions ask in ``#openstack-release``
