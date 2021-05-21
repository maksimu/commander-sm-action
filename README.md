# Keeper Commander GitHub Action

This action securely retrieves secrets from Keeper and places them to the desired destination of the runner such as 
environment variable, output parameters of the step or to the file.

## TL;DR

```yaml
on: 
  push:
    branches: [ master ]
    
jobs:
  buildexecutable:
    runs-on: ubuntu-latest
    name: Build with Keeper secrets
    steps:
      
      - name: Retrieve secrets from Keeper
        id: secrets_retrieval_step
        uses: maksimu/commander-sm-action@master
        with:
          keeper-secret-config: ${{ secrets.KEEPER_SECRET_KEY }}
          secrets: |
              uid123 password | PASSWORD
              uid234 password | env:PASSWORD
              uid234 password | out:PASSWORD
              uid234 field:login | out:login
              uid234 custom:Cust1 | env:CUST1
              uid321 file:config.json | file:~/to/file.json
              uid321 file:Certificate.crt | file:/usr/keeper/certs
    
      # Use the output from the `secrets_retrieval_step` step
      - name: Print login name
        run: echo "Login is ${{ steps.secrets_retrieval_step.outputs.login }}"
```

## Inputs

| Input                  | Required | Available Values                                                                                                                                                                                                                                                                      | Example                                                                                                                |   |
|------------------------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|---|
| `keeper-secret-config` | Yes      | n/a                                                                                                                                                                                                                                                                                   | `keeper-secret-config: ${{ secrets.KEEPER_SECRET_KEY }}`                                            |   |
| `secrets`              | Yes      |                                                                                                                                                                                                                                                                                       | ```yaml<br>secrets: \|<br><br>    uid123 password \| APP_PASSWORD<br><br>    uid234 password \| env:DB_PASSWORD<br>``` |   |
| `server`               | No       | - Host<br>  - `https://keepersecurity.com`<br>  - `keepersecurity.com`<br><br>- Abbreviation<br>  - `US` - Default: resolve to `keepersecurity.com` <br>  - `EU` - resolve to `keepersecurity.eu`<br>  - `AU` - resolve to `keepersecurity.com.au`<br>  - `US_GOV` - resolve to `TBD` | ```yaml<br>server: EU<br>```                                                                                           |   |
|                        |          |                                                                                                                                                                                                                                                                                       |                                                                                                                        |   |
## Outputs

Supported outputs of the secret:



## `secrets` format

`[secret uid] [secret field] | [destination]:[destination name OR location]`

### Secret uid
Unique secret's UID.

Example `YdA9mGHHer5a-4QNsEyVuz`. To find record UID


### Secret field
A field or a file to be retrieved from the secret

Available fields:
- `field:password`
- `field:login`
- `field:title`
- `custom:[Custom field name]`
- `file:[Name of a file]`

### Destination and Destination Name/Location
Destination of the secret value in GitHub Action

Available values:

- `env` - Output secret's value to the environment variable
  
  **Format of the destination:**

  - `ENV_VAR_NAME` - Just a name of the environment variable
  - `env:ENV_VAR_NAME` - Prepend `env:` to the begging to indicate the destination to be an environment variable

  Example:
  
  ```yaml
  - name: Retrieve secrets from Keeper
    uses: Keeper-Security/commander-actions@v1
    with:
      keeper-secret-config: ${{ secrets.KEEPER_SECRET_KEY }}
      secrets: |
          uid123 password | APP_PASSWORD
          uid234 password | env:DB_PASSWORD
  ```

- `out` - Output secret's value to the outputs parameters as of the steps as `outputs.<output_name>`

  **Format of the destination:**
  - `out:output_name` - Prepend `out:` to the beginning to indicate the destination to be outputs parameters of the step
  
  Example usage:
  
  ```yaml
  - name: Retrieve secrets from Keeper
    id: keeper_secrets_step
    uses: maksimu/commander-sm-action@master
    with:
      keeper-secret-config: ${{ secrets.KEEPER_SECRET_KEY }}
      secrets: |
          uid234 password | out:password
          uid234 field:login | out:login
  
  # Use the output from the `print step` step 
  # (Note: GitHub Actions will mask the output of the password)
  - name: Print password
    run: echo "Password is ${{ steps.keeper_secrets_step.outputs.password }}"
  ```

- `file` - Outputs secret's file to the file location on the current GitHub runner
  **Format of the destination:**
  - `file:[file location]` - Prepend `file:` to the beginning to indicate the destination to be a file
  
  Example usage:

  ```yaml
  - name: Retrieve secrets from Keeper
    uses: maksimu/commander-sm-action@master
    with:
      keeper-secret-config: ${{ secrets.KEEPER_SECRET_KEY }}
      secrets: |
          uid321 file:config.json | file:~/to/file.json
          uid321 file:Certificate.crt | file:/usr/keeper/certs
  ```
