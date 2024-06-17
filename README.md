# Congress Trades

Downloads all public finantial disclosures from the United States House of Representatives Disclosures Clerk website 
for the speficied members of congress, parses the pdf files, and spins up a dashboard for visualizing the information.

Specify date ranges and congress members in `config.yaml` file

```yaml
data:
  dir: data
  years:
    from: 2020
    to: 2024
  members:
    - gottheimer
    - goldman
    - tuberville
    - pelosi
    - scott
    - franklin
    - mullin
    - green
```

To download and parse disclosure information:

```
make get-data
```

![Dashboard Video](static/example.gif)


