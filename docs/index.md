```{toctree}
:caption: Documentation
:hidden:

installation
database
models
usage
```

```{toctree} 
:caption: External Links
:hidden:

GitHub Repo<https://github.com/dkadyrov/spidb>
Publication <https://www.mdpi.com/1424-8220/24/20/6736>
```


# Stored Product Insect Database

The Stored Product Insect Database (SPIDB) is the Python package to assist with the Stored Product Insect Dataset (SPID) available on Kaggle. The SPID dataset is a collection of recordings made using the Acoustic Stored Product Insect Detection System (A-SPIDS) and the Microwave Stored Product Insect Detection System (M-SPIDS) of several stored product insects at different life stages within various materials under different levels of artificial and natural noise. 

## Background

Stored products, such as grains, seeds, nuts, and processed foods, make up a large portion of the global food supply and trade are susceptible to infestation by a variety of insects. These insects, known as stored product pests (SPPs), can cause significant agricultural, environmental, and economic losses when they contaminate materials at any stage of the supply chain from farming, storage, processing, and distribution. When traded internationally, SPPs can also be a vector for the spread of invasive species and pathogens.

Stored product pests are grouped as internal, external, and secondary pests based on their feeding habits and the damage they cause. Internal feeders, such as the rice weevil, _Sitophilus oryzae_, bury into the kernel as larvae and eat the endosperm until they emerge as adults. External feeders, such as the red flour beetle, _Tribolium castaneum_, break down the surface of the kernel. Scavengers, such as the sawtoothed grain beetle _Oryzaephilus surinamensis_, feed on the broken kernels and other debris. Secondary pests, such as the mealworm, _Tenebrio molitor_, feed on the waste and debris left by the primary pests [^sps].

The ISO 6639 standard specifies that a container is infested if an insect is found within a one kilogram sample [^iso]. The USDA determines an infestation is one kilogram of product contains two or more live insects [^usda]. Although the main method for inspecting infestation is visual inspection, often with tools such as magnifying glasses and sieves, it is time-consuming and labor-intensive. Physical methods include probe traps, Berlese funnels, and pitfall traps, often used in conjunction with pheromones and light attractants. Automated sieves, electronic counters, electrical conductance machines, and flotation methods allow faster inspection of larger samples. Chemical methods include monitoring for CO2 and uric acid levels as well as employing the electric nose to detect for volatile compounds. Spectral imaging includes hyperspectral imaging, near-infrared spectroscopy, and X-ray imaging. Acoustic methods include the use of microphones, accelerometers, and acoustic emission sensors to detect the sounds of insects moving, feeding, and mating [^sensors]. These methods need to balance accurate detection and classification pests of various life stages with ensuring product quality, minimizing costs, and assuring efficiency of supply chain movement while limiting the amount of damage or loss during examination. 

The Acoustic Stored Product Insect Detection System (A-SPIDS) and the Microwave Stored Product Insect Detection System (M-SPIDS) were developed as a low-cost, portable, and non-destructive alternative method for detecting stored product insects.

[^sps]: G. Bennett, J. Owens, and R. Corrigan, “Truman’s Scientific Guide to Pest Control Operations,” 1988
[^iso]: International Organization for Standardization, “ISO 6639:1985 - Cereals - Determination of Insect Infestation of Cereals,” 1985
[^usda]: USDA, Grain Inspection Handbook. US Department of Agriculture, Marketing and Regulatory Programs, Grain Inspection, Packers and Stockyards Administration, Federal Grain Inspection Service, 2004.
[^sensors]: S. Neethirajan, C. Karunakaran, D. S. Jayas, and N. D. G. White, “Detection Techniques for Stored-Product Insects in Grain,” Food Control, vol. 18, no. 2, pp. 157–162, Feb. 2007, doi: 10.1016/j.foodcont.2005.09.008.
