.PHONY: clean all

all:
	as3ninja transform --pretty -o declaration.json -t template.j2 -c all_tenants.yaml

CookieCorp:
	as3ninja transform --pretty -o declaration.json -t template.j2 -c tenant_CookieCorp.yaml

CakeFactory:
	as3ninja transform --pretty -o declaration.json -t template.j2 -c tenant_CakeFactory.yaml

clean:
	rm -f declaration.json
