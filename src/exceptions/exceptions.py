class ModelNotTrained(Exception):
    pass

class TransitionsNeedAtLeastTwoStates(Exception):
    pass

class TagsLengthNeedsToBeGreaterThanK(Exception):
    pass

class TooShortStopRegionGroup(Exception):
    pass

class StateNotPresentInTrainAsOrigin(Exception):
    pass

class TopParentNotCategory(Exception):
    pass

class NoCategoryMatched(Exception):
    pass

class NotValidTypes(Exception):
    pass

class ContextNotFoundInLeavesMapKeys(Exception):
    pass

class ClusterSizeInadequate(Exception):
    pass