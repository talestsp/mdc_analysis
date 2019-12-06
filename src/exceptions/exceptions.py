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

class ValueFarFromOne(Exception):
    pass

class EmptyDirectory(Exception):
    pass

class StopRegionMinTimeNotLoaded(Exception):
    pass

class VersionNotRegistered(Exception):
    pass

class MinStopRegionTimeIs5Min(Exception):
    pass


