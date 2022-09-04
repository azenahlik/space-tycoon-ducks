# Example python space tycoon bot

! Fork this repository !

Install dependencies
```bash
pip install -r requirements.txt
```
 
Install the client
```bash
cd space_tycoon_generated_client
python setup.py install --user
```

## Docs
Located in `space_tycoon_generated_client/README.md` and `space_tycoon_generated_client/docs`

## Only when client API definition changes
Regenerate client code (docker is necessary)
```bash
sudo ./client-gen.sh
```
and then install the client again
