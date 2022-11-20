# dynamic iRule parameterization

This example shows how iRules can be dynamically parameterized using AS3 Ninja.

## Scenario

The task is to host the [2D breakout game using pure JavaScript](https://developer.mozilla.org/en-US/docs/Games/Tutorials/2D_Breakout_game_pure_JavaScript) based on the linked MDN article (also available [on Github](https://github.com/end3r/Gamedev-Canvas-workshop))

For increased security [SRI (Subresource Integrity)](https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity) should be added to the HTML script tag.
The actual javascript should be hosted separately at ``/game.js`` any other URI should return the HTML.

The javascript changes over the 10 lessons requiring us to calculate the integrity for each lesson.

## Solution

AS3 Ninja is used to parameterize the iRule and calculate the hash / digest dynamically based on the included javascript file.


To generate the declaration based on the jinja2 template and yaml configuration, run one of the below commands.

```shell
as3ninja transform -t declaration.j2 -c config.yaml

make
```
