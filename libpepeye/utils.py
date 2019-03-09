""" Routines that do type checking or create classes
"""
import logging, numbers

logger = logging.getLogger(__name__)


def check_class(obj, target_class, allow_none = False):
    """ Checks that the  obj is a (sub)type of target_class. 
        Raises a TypeError if this is not the case.

        :param obj: object whos type is to be checked
        :type obj: any type
        :param target_class: target type/class
        :type target_class: any class or type
        :param allow_none: if true obj may be None
        :type allow_none: boolean
    """
    if not isinstance(obj, target_class):
        if not (allow_none and obj is None):
            raise TypeError("obj must be a of type {}, got: {}"
                            .format(target_class, type(obj)))



def environment_var_to_bool(env_var):
    """ Converts an environment variable to a boolean

        Returns False if the environment variable is False, 0 or a case-insenstive string "false"
        or "0".
    """

    # Try to see if env_var can be converted to an int
    try:
        env_var = int(env_var)
    except ValueError:
        pass

    if isinstance(env_var, numbers.Number):
        return bool(env_var)
    elif isinstance(env_var, str):
        env_var = env_var.lower().strip()
        if env_var in "false":
            return False
        else:
            return True
    else:
        return bool(env_var)
