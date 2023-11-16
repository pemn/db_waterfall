## 📌 Description
create a standard waterfall chart between two datasets
## 📸 Screenshot
![screenshot1](../../code/pandoc_index/assets/db_waterfall1.png)
## 📝 Parameters
name|optional|description
---|---|------
input_a,input_b|❎|path to data in a supported format
groups_a,groups_b|❎|group fields for comparison
value_a,value_b|❎|numeric field for totals
condition|☑️|only rows that evaluate to true will be used
output|☑️|path to save the buildup chart as png
display||show the result in a popup window

## 📓 Notes
 - The data must already be aggregated (each combination of groups only has one value)
 
## 📚 Examples
![screenshot2](../../code/pandoc_index/assets/db_waterfall2.png)
## 🧩 Compatibility
distribution|status
---|---
![winpython_icon](../../code/pandoc_index/assets/winpython_icon.png)|✔
![vulcan_icon](../../code/pandoc_index/assets/vulcan_icon.png)|❓
![anaconda_icon](../../code/pandoc_index/assets/anaconda_icon.png)|❌
## 🙋 Support
Any question or problem contact:
 - paulo.ernesto
## 💎 License
Apache 2.0
Copyright ![vale_logo_only](../../code/pandoc_index/assets/vale_logo_only_r.svg) Vale 2023