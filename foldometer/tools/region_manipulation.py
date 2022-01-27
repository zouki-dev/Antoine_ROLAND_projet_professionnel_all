import pandas as pd
import numpy as np

def clean_mask_one_block(mask):
    def longestConsecutive(nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        if not nums:
            return 0
        nums = list(dict.fromkeys(nums))
        nums.sort()
        maxCount=0
        count = 1
        block = []
        blockMax = None
        for index, value in enumerate(nums):
            if index + 1 >= len(nums):
                break
            if nums[index + 1] == value + 1:
                count += 1
                block.append(value)
            else:
                block.append(value)
                if count>maxCount:
                    blockMax = block
                count = 1
                block = []
        return blockMax

    blockMax = longestConsecutive(list(np.where(mask)[0]))

    maskMaker = np.zeros(len(mask))
    maskMaker[blockMax] = 1
    maskCleaned = np.array(maskMaker, dtype=bool)
    return maskCleaned

def get_cycle_region_time_sorted(data):
    pullingCycles = data["pullingCycle"].unique()
    cycleRegion = []
    timeList = []
    for pullingCycle in pullingCycles:
        for region in ["pulling", "retracting", "stationary"]:
            mask = (data["region"] == region)&(data["pullingCycle"] == pullingCycle)
            if not data["time"].loc[mask].empty:
                cycleRegion.append((int(pullingCycle), region, mask))
                timeList.append(data["time"].loc[mask].mean())
    indexOrder = sorted(range(len(timeList)), key=lambda k: timeList[k])
    sortedCycleRegion = [cycleRegion[i] for i in indexOrder]
    return sortedCycleRegion

def get_cycle_region_pulling_then_retracting(data):
    pullingCycles = data["pullingCycle"].unique()
    cycleRegion = []
    timeList = []
    for region in ["pulling", "retracting", "stationary"]:
        for pullingCycle in pullingCycles:
            mask = (data["region"] == region)&(data["pullingCycle"] == pullingCycle)
            if not data["time"].loc[mask].empty:
                cycleRegion.append((int(pullingCycle), region, mask))
    return cycleRegion

def get_cycle_region_by_cycle_previous_retracting(data):
    pullingCycles = data["pullingCycle"].unique()
    cycleRegion = []
    timeList = []
    for pullingCycle in pullingCycles:
        for region in ["pulling", "retracting", "stationary"]:
            mask = (data["region"] == region)&(data["pullingCycle"] == pullingCycle)
            if not data["time"].loc[mask].empty:
                cycleRegion.append((int(pullingCycle), region, mask))
                timeList.append(data["time"].loc[mask].mean())
    indexOrder = sorted(range(len(timeList)), key=lambda k: timeList[k])
    sortedCycleRegion = [cycleRegion[i] for i in indexOrder]

    cycles = []
    cycle = {}
    for (pullingCycle, region, mask) in sortedCycleRegion:
        cycle[region] = (pullingCycle, region, mask)
        if region == "pulling":
            cycles.append(cycle)
            cycle = {}
    return cycles #list of dico 'retracting' 'stationary' 'pulling' previous retracting

def get_cycle_region_by_cycle_next_retracting(data):
    pullingCycles = data["pullingCycle"].unique()
    cycleRegion = []
    timeList = []
    for pullingCycle in pullingCycles:
        for region in ["pulling", "retracting", "stationary"]:
            mask = (data["region"] == region) & (data["pullingCycle"] == pullingCycle)
            if not data["time"].loc[mask].empty:
                cycleRegion.append((int(pullingCycle), region, mask))
                timeList.append(data["time"].loc[mask].mean())
    indexOrder = sorted(range(len(timeList)), key=lambda k: timeList[k])
    sortedCycleRegion = [cycleRegion[i] for i in indexOrder]

    cycles = []
    cycle = {}
    for (pullingCycle, region, mask) in sortedCycleRegion:
        cycles.append((pullingCycle, region, mask))
        cycle = {}
    return cycles  # list of dico 'retracting' 'stationary' 'pulling' next retracting

def get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting(data):
    pullingCycles = data["pullingCycle"].unique()
    cycleRegion = []
    timeList = []
    for pullingCycle in pullingCycles:
        for region in ["pulling", "retracting", "stationary"]:
            mask = (data["region"] == region)&(data["pullingCycle"] == pullingCycle)
            if not data["time"].loc[mask].empty:
                cycleRegion.append((int(pullingCycle), region, mask))
                timeList.append(data["time"].loc[mask].mean())
    indexOrder = sorted(range(len(timeList)), key=lambda k: timeList[k])
    sortedCycleRegion = [cycleRegion[i] for i in indexOrder]

    cycles = []
    cycle = {"retracting": (-1, "retracting", data["time"] < 0),\
             "stationary": (-1, "stationary", data["time"] < 0),\
             "pulling": (-1, "pulling", data["time"] < 0),\
             "nextRetracting": (-1, "retracting", data["time"] < 0)}
    thereIsPullingInCycle = False
    isSmthToAppend = False
    for (pullingCycle, region, mask) in sortedCycleRegion:
        if region == "pulling":
            cycle["pulling"] = (pullingCycle, region, mask)
            thereIsPullingInCycle = True
            isSmthToAppend = True

        if region == "retracting" and thereIsPullingInCycle:
            cycle["nextRetracting"] = (pullingCycle, region, mask)
            cycles.append(cycle)

            cycle = {"retracting": (pullingCycle, region, mask),\
                     "stationary": (-1, "stationary", data["time"] < 0),\
                     "pulling": (-1, "pulling", data["time"] < 0),\
                     "nextRetracting": (-1, "retracting", data["time"] < 0)}
            thereIsPullingInCycle = False
            isSmthToAppend = False

        if region == "stationary":
            cycle["stationary"] = (pullingCycle, region, mask)
            isSmthToAppend = True

    if isSmthToAppend:
        cycles.append(cycle)

    return cycles #list of dico 'retracting' 'stationary' 'pulling' 'nextRetracting'
