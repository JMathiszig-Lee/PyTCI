def james(height: float, weight: float, sex: str) -> float:
    """ returns lean body mass as per james equations """
    # TODO provide reference

    if sex != "m" and sex != "f":
        raise ValueError(
            "Unknown sex '%s'. This algorithm can only handle 'm' and 'f'. :(" % sex
        )

        # TODO: Use better equation to calculate lean body mass
        if sex == "m":
            return 1.1 * weight - 128 * ((weight / height) * (weight / height))
        else:
            return 1.07 * weight - 148 * ((weight / height) * (weight / height))
