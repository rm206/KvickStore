# KvickStore

Love puns? Love lighweight and safe key-value stores? Then you'll love KvickStore!

KvickStore is a simple and lightweight key-value store based on the [json](https://docs.python.org/3/library/json.html) module. It has been __heavily__ inspired by [pickleDB](https://github.com/patx/pickledb/) but I aim to make it more flexible.

<br/>

# KvickStore is easy to use

```python
>>> import KvickStore

>>> db = KvickStore.load('test.db', False)

>>> db.set('key', 'value')

>>> db.get('key')
'value'

>>> db.save()
True
```
<br/>

# Link(s)
* [GitHub repo](https://github.com/rm206/KvickStore)

<br/>

# Notes
This is a project under development. I plan to add more features and make it more robust. 
If you have any suggestions or feedback, please let me know! I would love to hear and learn from you.