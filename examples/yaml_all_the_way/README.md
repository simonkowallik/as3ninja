# yaml (almost) all the way

This example uses a YAML for all configurations with a minimal AS3 Ninja jinja2 template.

This provides the full and unconstrained flexibility of AS3, all formatted in YAML.


## generating declarations

You can generate tenant specific declarations or one delcaration for all tenants using the below commands.

```shell
as3ninja transform --pretty -o declaration.json -t template.j2 -c all_tenants.yaml

as3ninja transform --pretty -o declaration.json -t template.j2 -c tenant_CookieCorp.yaml

as3ninja transform --pretty -o declaration.json -t template.j2 -c tenant_CakeFactory.yaml
```
