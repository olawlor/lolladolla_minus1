# Manage lolladollas using a Python web server
#  Run with
#    python3 lolladolla.py

from circuits.web import Server, Controller, Logger
import shelve
import re

class lolladollaAccount:
	def __init__(self,name,pubkey,signkey,balance):
		self.name=name;
		self.pubkey=pubkey;
		self.signkey=signkey;
		self.balance=balance;

# We're using the Python storage "shelve" for persistent data storage.
#   accounts[pubkey] = lolladollaAccount
accounts=shelve.open("lolladolla.accounts",'c',None,True)

# Magically grant dollars to reserve account:
#accounts["9000"].balance=10000000000.0;
#accounts.sync();

namePattern=re.compile('^[0-9a-zA-Z .]+$')
def nameValid(name):
	"""Check if this could be a valid username, and throw if not OK"""
	if not isinstance(name,str):
		raise ValueError("Name '"+name+"' needs to be a string (currently a "+type(str)+")")
	if re.search(namePattern,name) is None:
		raise ValueError("Name '"+name+"' does not match accepted pattern")

pubkeyPattern=re.compile('^[0-9a-fA-F:]+$')
def pubkeyValid(pubkey):
	"""Check if this could be a valid public key, and throw if not OK"""
	if not isinstance(pubkey,str):
		raise ValueError("Pubkey '"+pubkey+"' needs to be a string (currently a "+type(str)+")")
	if re.search(pubkeyPattern,pubkey) is None:
		raise ValueError("Pubkey '"+pubkey+"' does not match accepted pattern")


def pubkeyExists(pubkey):
	"""Check this account public key already exists, and throw an error if it's not OK"""
	pubkeyValid(pubkey)
	if not pubkey in accounts:
		raise ValueError("Pubkey '"+pubkey+"' not found in account list")
	return accounts[pubkey]

class lolladollaServer(Controller):
	"""Serve web requests for lolladollas"""
	def _trace(self,string):
		print("lolladolla> "+string)
	
	def balance(self,pubkey=""):
		self._trace("balance check on "+pubkey)
		a=pubkeyExists(pubkey)
		return "{'balance':%.2f, 'public_key':'%s', 'name':'%s'}" % (a.balance,a.pubkey,a.name)

	def dump(self):
		str="List of account names, public keys, and balances:<br><ul>\n"
		for pubkey in accounts:
			a=accounts[pubkey]
			str+="<li>balance %.2f   public_key %s   name %s" % (a.balance,a.pubkey,a.name)
		str+="</ul>\n"
		return str
	
	def create(self,name="",pubkey="",signkey=""):
		self._trace("Create new account name: "+name+" pubkey: "+pubkey)
		nameValid(name);
		pubkeyValid(pubkey);
		if not isinstance(signkey,str):
			return "signkey needs to be a string";
		if pubkey in accounts:
			return "pubkey "+pubkey+" already exists, ignoring create request";

		accounts[pubkey]=lolladollaAccount(name,pubkey,signkey,0.0)
		accounts.sync()
		return "Created account"

	def xfer(self,srcpubkey="",amount=0.0,destpubkey="",signature=""):
		self._trace("xfer "+amount+" from "+srcpubkey+" to "+destpubkey+" with signature "+signature)
		src=pubkeyExists(srcpubkey)
		dest=pubkeyExists(destpubkey)
		amount=float(amount);
		if not isinstance(amount,float):
			return "Amount needs to be a float";
		if not isinstance(signature,str):
			return "Signature needs to be a string";
		
		# FIXME: use secret key encryption here?
		if signature!=src.signkey:
			return "Signature does not match";
		
		src.balance -= amount;
		dest.balance += amount;
		accounts.sync()
		return "Transfer complete"
		
	def index(self):
		return """\
<html><head></head>
<body>
<h1>&#8356; Server</h1>

<h2>Show All Account Balances</h2>
<form action="dump" method="POST">
<input type="submit" value="Show All">
</form>

<h2>Create an Account</h2>
<form action="create" method="POST">
<input type="text" name="name"> Account Name<br>
<input type="text" name="pubkey"> Public Key<br>
<input type="password" name="signkey"> Signing Key<br>
<br>
<input type="submit" value="Create Account">
</form>

<h2>Transfer Funds</h2>
<form action="xfer" method="POST">
<input type="text" name="srcpubkey"> Source Account Public Key<br>
<input type="password" name="signature"> Source Account Signing Key<br>
<input type="text" name="destpubkey"> Destination Account Public Key<br>
Transfer amount: <input type="text" name="amount">&#8356;<br>
<br>
<input type="submit" value="Transfer Funds">
</form>

<hr>
lolladolla server version -1.04
</body>
</html>
"""

app = Server(("0.0.0.0",8080))
lolladollaServer().register(app)
app += Logger()
app.run()


