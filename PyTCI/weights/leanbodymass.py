def james(height: float, weight: float, sex: str) -> float:
    """ returns lean body mass as per james equations """
    """James, W. "Research on obesity: a report of the DHSS/MRC group" HM Stationery Office 1976"""

    if sex != "m" and sex != "f":
        raise ValueError(
            "Unknown sex '%s'. This algorithm can only handle 'm' and 'f'. :(" % sex
        )

    if sex == "m":
        return 1.1 * weight - 128 * ((weight / height) * (weight / height))
    else:
        return 1.07 * weight - 148 * ((weight / height) * (weight / height))


def boer(height: float, weight: float, sex: str) -> float:
    """ returns lean body mass as per Boer equation """
    """ Boer P. "Estimated lean body mass as an index for normalization of body fluid volumes in man." Am J Physiol 1984; 247: F632-5"""

    if sex != "m" and sex != "f":
        raise ValueError(
            "Unknown sex '%s'. This algorithm can only handle 'm' and 'f'. :(" % sex
        )

    if sex == "m":
        lbm = (0.407 * weight) + (0.267 * height) - 19.2
    else:
        lbm = (0.252 * weight) + (0.473 * height) - 48.3

    return round(lbm, 1)


def hume66(height: float, weight: float, sex: str) -> float:
    """ returns lean body mass as per the 1966 Hume paper """
    """ Hume, R "Prediction of lean body mass from height and weight.". J Clin Pathol. 1966 Jul; 19(4):389-91"""

    if sex != "m" and sex != "f":
        raise ValueError(
            "Unknown sex '%s'. This algorithm can only handle 'm' and 'f'. :(" % sex
        )

    if sex == "m":
        lbm = (0.32810 * weight) + (0.33929 * height) - 29.5336
    else:
        lbm = (0.29569 * weight) + (0.41813 * height) - 43.2933

    return round(lbm, 1)


def hume71(height: float, weight: float, sex: str) -> float:
    """ returns lean body mass from Hume & Weyers(1971) """
    """ Relationship between total body water and surface area in normal and obese subjects. Hume R, Weyers E J Clin Pathol 24 p234-8 (1971 Apr) """

    if sex != "m" and sex != "f":
        raise ValueError(
            "Unknown sex '%s'. This algorithm can only handle 'm' and 'f'. :(" % sex
        )

    if sex == "m":
        lbm = (0.4066 * weight) + (0.2668 * height) - 19.19
    else:
        lbm = (0.2518 * weight) + (0.4720 * height) - 48.32

    return round(lbm, 1)


def janmahasation(height: float, weight: float, sex: str) -> float:
    """ lean body mass as per Janmahasation / Han 2005 """

    if sex != "m" and sex != "f":
        raise ValueError(
            "Unknown sex '%s'. This algorithm can only handle 'm' and 'f'. :(" % sex
        )
    bodymass = bmi(height, weight)

    if sex == "m":
        lbm = (9270 * weight) / (6680 + 216 * bodymass)
    else:
        lbm = (9270 * weight) / (8780 + 244 * bodymass)

    return round(lbm, 1)


def bmi(height: float, weight: float) -> float:
    """calculates BMI"""
    bmi = weight / ((height / 100) ** 2)
    return round(bmi, 1)


def idealbodyweight(height: float, sex: str) -> float:
    """ ideal body weight as per ARDSnet/Devine  """

    if sex != "m" and sex != "f":
        raise ValueError(
            "Unknown sex '%s'. This algorithm can only handle 'm' and 'f'. :(" % sex
        )

    if sex == "m":
        ibm = 50.0 + 0.91 * (height - 152.4)
    else:
        ibm = 45.5 + 0.91 * (height - 152.4)

    return round(ibm, 1)


def adjustedbodyweight(height: float, weight: float, sex: str) -> float:
    """ adjusted body weight for obese patients """

    ibw = idealbodyweight(height, sex)
    abw = ibw + 0.4 * (weight - ibw)

    return round(abw, 1)
