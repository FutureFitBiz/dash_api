import uuid
import datetime

from app import bcrypt, db
import models as m
import lib.common_utils as common_utils

stakeholder_name_question = 'A-1'
intensity_duration = 'A-17'
intensity_significance = 'A-18'
intensity_proportion = 'A-21'
scale_question = 'A-15'
scale_unit = 'people'
depth_value_question = 'A-9'
depth_unit_question = 'A-10'

COMPLETE = 'complete'
INCOMPLETE = 'incomplete'
NOT_RELEVANT = 'not relevant'
NO_DATA = 'no data'

goal_status_to_order = {
    COMPLETE: 1,
    INCOMPLETE: 2,
    NOT_RELEVANT: 4,
    NO_DATA: 5,
}

risk_priority = {
    common_utils.HIGHEST_RISK: 666,
    common_utils.LOW_RISK: 5,
    common_utils.HIGH_RISK: 4,
    common_utils.MODERATE_RISK: 3,
    common_utils.UNLIKELY_RISK: 2,
}

break_evens = ['BE01', 'BE02', 'BE03', 'BE04', 'BE05', 'BE06', 'BE07', 'BE08', 'BE09', 'BE10', 'BE11',
               'BE12', 'BE13', 'BE14', 'BE15', 'BE16', 'BE17', 'BE18', 'BE19', 'BE20', 'BE21', 'BE22', 'BE23']

sdg_links = {
    'BE01':	[7, 13],
    'BE02':	[6, 12, 14, 15],
    'BE03':	[1, 2, 8, 12, 14, 15],
    'BE04':	[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
    'BE05':	[3, 6, 11, 12, 14, 15],
    'BE06':	[13	],
    'BE07': [11, 12, 14],
    'BE08':	[1, 6, 11, 13, 14, 15],
    'BE09':	[11, 16],
    'BE10':	[2, 3, 5, 6, 8]	,
    'BE11':	[1, 2, 3, 6, 8, 10, 11],
    'BE12':	[5, 8],
    'BE13':	[5, 10],
    'BE14':	[5, 10, 16],
    'BE15':	[12	],
    'BE16':	[12, 16	],
    'BE17':	[3, 6, 11, 12, 14],
    'BE18':	[13	],
    'BE19':	[11, 12, 14	],
    'BE20':	[16	],
    'BE21':	[9, 10],
    'BE22':	[16],
    'BE23':	[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
}


be_heading_text = {
    'BE01': "A Future-Fit Business ensures that all energy consumed – as electricity, heat or fuel – is derived from renewable energy sources: solar, wind, ocean, hydropower, geothermal resources, and biomass.",
    'BE02': 'A Future-Fit Business protects freshwater resources by minimizing water consumption in its commercial and industrial activities, and by ensuring its discharges do not degrade the water quality of receiving watersheds.',
    'BE03': 'A Future-Fit Business preserves the health of all natural resources it directly manages, as well as that of all ecosystems and communities impacted by sourcing activities it conducts itself (e.g. farming, fishing, hunting, rearing animals, mining).',
    'BE04': 'A Future-Fit Business seeks to reduce – and eventually eliminate – any negative environmental and social impact caused by the goods and services it depends upon, by continuously striving to anticipate, avoid and address issue-specific hotspots in its supply chains.',
    'BE05': 'A Future-Fit Business eliminates all forms of harmful emissions from its operations – gaseous, liquid and solid.',
    'BE06': 'A Future-Fit Business emits net zero GHGs as a result of its own operational activities, including energy it consumes.',
    'BE07': 'A Future-Fit Business seeks to eliminate operational waste completely, and ensures that all by-products are repurposed. Organic waste may be composted and returned to the soil, and materials that can be reused must be reclaimed.',
    'BE08': 'A Future-Fit Business preserves the health of all areas of high biological, ecological, social or cultural value – both by protecting them where the company is already active, and by avoiding further expansion into new areas if degradation is possible.',
    'BE09': 'A Future-Fit Business actively seeks to anticipate, avoid and address the concerns of all local communities whose wellbeing may be affected by its operational activities.',
    'BE10': 'A Future-Fit Business safeguards the health of its employees by ensuring physically safe work environments, having zero tolerance for harassment and bullying, and by nurturing emotional and mental wellbeing.',
    'BE11': 'A Future-Fit Fit Business pays all workers in all regions enough to meet their basic needs and secure essential services for themselves and their families.',
    'BE12': 'A Future-Fit Business ensures that all its workers are treated fairly. Contracts between employer and employee afford individuals the basic protections, freedoms and rights expected in a prosperous and just society.',
    'BE13': 'A Future-Fit Business proactively investigates and monitors key practices – such as recruitment, pay structures, hiring, performance assessment and promotions – to ensure that no discrimination occurs, however unintentional it may be.',
    'BE14': 'A Future-Fit Business takes steps to minimize employee concerns, and implements processes and policies to identify and deal fairly with any issues that do arise.',
    'BE15': 'A Future-Fit Business does everything it can to help customers make responsible decisions regarding the purchase, use and (in the case of physical goods) post-use processing of its products. In addition, it markets its products honestly and ethically to appropriate audiences.',
    'BE16': 'A Future-Fit Business gives a voice to its customers by actively soliciting any concerns they have, impartially investigating them, and fairly and transparently acting to address legitimate grievances.',
    'BE17': 'A Future-Fit Business ensures all of the products it offers are completely benign to people and nature, both during use and (in the case of physical goods) as a result of their post-use processing.',
    'BE18': 'A Future-Fit Business sells no goods or services that emit greenhouse gases as a direct consequence of their use.',
    'BE19': 'A Future-Fit Business does all it can to ensure that the physical goods it provides to others can be repurposed at the end of their useful life.',
    'BE20': 'A Future-Fit Business actively seeks to anticipate, avoid and address ethical breaches that may arise as a result of its activities.',
    'BE21': 'A Future-Fit Business commits publicly to a responsible tax policy, and works continuously to ensure that it lives up to this policy, across all its areas of business.',
    'BE22': 'A Future-Fit Business never seeks to influence market dynamics in ways that may contribute to hindering society’s progress toward future-fitness.',
    'BE23': 'A Future-Fit Business implements investment policies and processes that continuously seek to improve the future-fitness of both the financial assets it owns, and any that it manages or controls on behalf of third-party asset owners.',
}


sdgs = {
    '1': {
        'title': 'No Poverty',
        'text': 'End poverty in all forms everywhere',
    },
    '2': {
        'title': 'Zero Hunger',
        'text': 'End hunger, achieve food security and improved nutrition and promote sustainable agriculture',

    },
    '3': {
        'title': 'Good Health and Well-Being',
        'text': 'Ensure healthy lives and promote well-being for all at all ages',

    },
    '4': {
        'title': 'Quality Education',
        'text': 'Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all',

    },
    '5': {
        'title': 'Gender Equality',
        'text': 'Achieve gender equality and empower all woman and girls',

    },
    '6': {
        'title': 'Clean Water and Sanitation',
        'text': 'Ensure availability and sustainable management of water and sanitation for all',

    },
    '7': {
        'title': 'Affordable and Clean Energy',
        'text': 'Ensure access to affordable, reliable, sustainable and modern energy for all',

    },
    '8': {
        'title': 'Decent Work and Economic Growth',
        'text': 'Promote sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all',

    },
    '9': {
        'title': 'Industry, Innovation and Infrastructure',
        'text': 'Build resilient infrastructure, promote inclusive and sustainable industrialisation and foster innovation',

    },
    '10': {
        'title': 'Reduced Inequalities',
        'text': 'Reduce inequality within and among countries',
    },
    '11': {
        'title': 'Sustainable Cities and Communities',
        'text': 'Make cities and human settlements inclusive, safe, resilient and sustainable',

    },
    '12': {
        'title': 'Responsible Consumption and Production',
        'text': 'Ensure sustainable consumption and production patterns',

    },
    '13': {
        'title': 'Climate Action',
        'text': 'Take urgent action to combat climate change and its impacts',

    },
    '14': {
        'title': 'Life Below Water',
        'text': 'Conserve and sustainably use the oceans, seas and marine resources for sustainable development',

    },
    '15': {
        'title': 'Life on Land',
        'text': 'Protect, restore and promote sustainable use of terrestrial ecosystems, sustainably manage forests, combat desertification, and halt and reverse land degradation and halt biodiversity loss',

    },
    '16': {
        'title': 'Peace, Justice and Strong Institutions',
        'text': 'Promote peaceful and inclusive societies for sustainable development, provide access to justice for all and build effective, accountable and inclusive institutions at all levels',

    },
    '17': {
        'title': 'Partnerships',
        'text': 'Strengthen the means of implementation and revitalise the global partnership for sustainable development',

    },
}


def get_be_sdg_links(code):
    return str(sdg_links[code])[1:-1]


individual_stakeholder_options = [
    'A-1.1',  # Customers (Individuals)
    'A-1.3',  #  Indirect Consumers/Community Members
    'A-1.4'  # Employees
]

scale_depth_units = {
    'A-1.1': 'Customers',
    'A-1.3': 'Indirect Consumers',
    'A-1.4': 'Employees',
}

ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def reporting_period_text(benchmark):
    return "{}, {} to {}".format(
        benchmark.start_date.year if benchmark.start_date else '----',
        benchmark.start_date.strftime('%B') if benchmark.start_date else '--',
        benchmark.end_date.strftime('%B') if benchmark.end_date else '--')


def from_js_date(str):
    str = str.replace('Z', '+00:00')
    return datetime.datetime.fromisoformat(str)


def to_js_date(dt):
    res = ''
    if dt:
        res = dt.strftime('%Y-%m-%d %H:%M:%SZ')
    return res


def sdg_key(key):
    if key:
        num = key.split('.')[0]
        return int(num)
    else:
        return 99999


def new_bcrypt_password(pw=None):
    if not pw:
        pw = random_uuid_code()
    return bcrypt.generate_password_hash(pw).decode('utf - 8')


def random_uuid_code(length=10):
    return str(uuid.uuid4()).replace('-', '')[0:length]


chart_bg_colours = [
    'rgba(54, 162, 235, 0.2)',  # // blue
    'rgba(255, 159, 64, 0.2)',  # //orange
    'rgba(75, 192, 192, 0.2)',  # // green
    'rgba(255, 99, 132, 0.2)',  # // red
    'rgba(255, 206, 86, 0.2)',  # // yello
    'rgba(153, 102, 255, 0.2)',  # // purple
]

chart_border_colours = [
    'rgba(54, 162, 235, 1)',  # // blue
    'rgba(255, 159, 64, 1)',  # // orange
    'rgba(75, 192, 192, 1)',  # // green
    'rgba(255, 99, 132, 1)',  # // red
    'rgba(255, 206, 86, 1)',  # // yello
    'rgba(153, 102, 255, 1)',  # // purple
]
