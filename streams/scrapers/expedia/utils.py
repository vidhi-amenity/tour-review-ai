from dateutil import parser
import re
import hashlib
def clean_date(str_date):
    try:
        return parser.parse(str_date, fuzzy=True)
    except:
        return None


def clean_rating(string):
    if string:
        rating, out_of = string.split('/')

        if out_of.startswith('10'):
            return int(rating) / 2
        else:
            return rating

    return None

def remove_emoji(text):
    if text == 'No written review provided':
        return ''
    # filtrare gli emoji non supportati
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticon
        u"\U0001F300-\U0001F5FF"  # simboli & pictogram
        u"\U0001F680-\U0001F6FF"  # trasporti & simboli
        u"\U0001F1E0-\U0001F1FF"  # bandiere (Unicode 6.0)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def generate_id(text):
    hash_object = hashlib.sha256(text.encode())
    return hash_object.hexdigest()[:20]


HEADERS = {
    'authority': 'www.expedia.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,ur;q=0.8',
    'client-info': 'lx-nimble,f75d311ecdb980880098cfa7ed9c07e62aa8bbc9,us-west-2',
    'content-type': 'application/json',
    'origin': 'https://www.expedia.com',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'x-page-id': 'page.LX.Infosite.Information,A,30',
}

# type 1
ACTIVITY_PAYLOAD = [
    {
        'operationName': 'ActivityReviewsDialogContentLazyQuery',
        'variables': {
            'activityId': '168417',
            'pagination': {
                'startingIndex': 0,
                'size': 100,
            },
            'context': {
                'siteId': 1,
                'locale': 'en_US',
                'eapid': 0,
                'currency': 'USD',
                'device': {
                    'type': 'DESKTOP',
                },
                'identity': {
                    'duaid': '6166c0cb-6146-4f0b-93f9-5c1ac6455017',
                    'expUserId': '-1',
                    'tuid': '-1',
                    'authState': 'ANONYMOUS',
                },
                'privacyTrackingState': 'CAN_TRACK',
                'debugContext': {
                    'abacusOverrides': [],
                    'alterMode': 'RELEASED',
                },
            },
        },
        'query': 'query ActivityReviewsDialogContentLazyQuery($context: ContextInput!, $activityId: String!, $selections: [ActivitySelectedValueInput!], $pagination: PaginationInput, $shoppingPath: ShoppingPathType) {\n  activityReviews(\n    context: $context\n    activityId: $activityId\n    selections: $selections\n    pagination: $pagination\n    shoppingPath: $shoppingPath\n  ) {\n    reviewsDialog {\n      ...ActivityReviewsDialogContentFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ActivityReviewsDialogContentFragment on ActivityReviewListComponent {\n  comments {\n    ...ActivityReviewsCommentFragment\n    __typename\n  }\n  summary {\n    ...ActivityReviewsSummaryFragment\n    __typename\n  }\n  sortTabs {\n    ...ActivityReviewsSortTabFragment\n    __typename\n  }\n  moreButton {\n    ...ActivityReviewsMoreButtonFragment\n    __typename\n  }\n  __typename\n}\n\nfragment ActivityReviewsCommentFragment on ActivityReview {\n  text\n  author\n  formattedActivityDate\n  overallScoreMessage {\n    ...EGDSTextFragment\n    __typename\n  }\n  formattedSubmissionDate\n  reviewedOn\n  userLocation\n  expando {\n    ...EGDSExpandoFragment\n    __typename\n  }\n  __typename\n}\n\nfragment EGDSExpandoFragment on EGDSExpando {\n  ... on EGDSExpandoPeek {\n    ...EGDSExpandoPeekFragment\n    __typename\n  }\n  ... on EGDSExpandoListItem {\n    ...EGDSExpandoListItemFragment\n    __typename\n  }\n  __typename\n}\n\nfragment EGDSExpandoPeekFragment on EGDSExpandoPeek {\n  expandAnalytics {\n    linkName\n    referrerId\n    __typename\n  }\n  expandedLabel\n  expandedAccessibilityText\n  collapsedAccessibilityText\n  collapseAnalytics {\n    linkName\n    referrerId\n    __typename\n  }\n  collapsedLabel\n  expanded\n  __typename\n}\n\nfragment EGDSExpandoListItemFragment on EGDSExpandoListItem {\n  collapseAnalytics {\n    linkName\n    referrerId\n    __typename\n  }\n  collapsedLabel\n  expandAnalytics {\n    linkName\n    referrerId\n    __typename\n  }\n  expandedLabel\n  expanded\n  __typename\n}\n\nfragment EGDSTextFragment on EGDSText {\n  ...EGDSHeadingFragment\n  ...EGDSPlainTextFragment\n  ...EGDSStylizedTextFragment\n  ...EGDSIconTextFragment\n  ...EGDSGraphicTextFragment\n  ...EGDSParagraphFragment\n  ...EGDSStandardLinkFragment\n  ...EGDSInlineLinkFragment\n  ...EGDSSpannableTextFragment\n  __typename\n}\n\nfragment EGDSHeadingFragment on EGDSHeading {\n  text\n  headingType\n  accessibility\n  __typename\n}\n\nfragment EGDSPlainTextFragment on EGDSPlainText {\n  text\n  __typename\n}\n\nfragment EGDSStylizedTextFragment on EGDSStylizedText {\n  text\n  theme\n  weight\n  accessibility\n  decorative\n  __typename\n}\n\nfragment EGDSIconTextFragment on EGDSIconText {\n  icon {\n    ...EGDSIconFragment\n    __typename\n  }\n  text\n  __typename\n}\n\nfragment EGDSIconFragment on Icon {\n  description\n  id\n  size\n  theme\n  title\n  withBackground\n  __typename\n}\n\nfragment EGDSGraphicTextFragment on EGDSGraphicText {\n  graphic {\n    ...EGDSGraphicFragment\n    __typename\n  }\n  text\n  __typename\n}\n\nfragment EGDSGraphicFragment on UIGraphic {\n  ... on Icon {\n    ...EGDSIconFragment\n    __typename\n  }\n  ... on Mark {\n    ...EGDSMarkFragment\n    __typename\n  }\n  __typename\n}\n\nfragment EGDSMarkFragment on Mark {\n  description\n  id\n  markSize: size\n  url {\n    ... on HttpURI {\n      __typename\n      relativePath\n      value\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment EGDSParagraphFragment on EGDSParagraph {\n  text\n  style\n  __typename\n}\n\nfragment EGDSStandardLinkFragment on EGDSStandardLink {\n  action {\n    accessibility\n    analytics {\n      linkName\n      referrerId\n      __typename\n    }\n    resource {\n      value\n      ... on HttpURI {\n        relativePath\n        __typename\n      }\n      __typename\n    }\n    target\n    useRelativePath\n    __typename\n  }\n  disabled\n  standardLinkIcon: icon {\n    ...EGDSIconFragment\n    __typename\n  }\n  iconPosition\n  size\n  text\n  __typename\n}\n\nfragment EGDSInlineLinkFragment on EGDSInlineLink {\n  action {\n    accessibility\n    analytics {\n      linkName\n      referrerId\n      __typename\n    }\n    resource {\n      value\n      __typename\n    }\n    target\n    __typename\n  }\n  disabled\n  size\n  text\n  __typename\n}\n\nfragment EGDSSpannableTextFragment on EGDSSpannableText {\n  text\n  contents {\n    ...EGDSSpannableTextContentFragment\n    __typename\n  }\n  inlineContent {\n    ...EGDSSpannableTextContentFragment\n    __typename\n  }\n  __typename\n}\n\nfragment EGDSSpannableTextContentFragment on EGDSText {\n  ...EGDSStylizedTextFragment\n  ...EGDSGraphicTextFragment\n  ...EGDSPlainTextFragment\n  __typename\n}\n\nfragment ActivityReviewsSummaryFragment on ActivityReviewsSummary {\n  averageScore {\n    ...EGDSTextFragment\n    __typename\n  }\n  disclaimer {\n    ...ActivityDisclaimerDialogFragment\n    __typename\n  }\n  sectionRef\n  __typename\n}\n\nfragment ActivityDisclaimerDialogFragment on ActivityDisclaimerDialog {\n  contents {\n    ...EGDSTextFragment\n    __typename\n  }\n  dialog {\n    closeAnalytics {\n      linkName\n      referrerId\n      __typename\n    }\n    footer {\n      ...EGDSDialogFooterFragment\n      __typename\n    }\n    __typename\n  }\n  trigger {\n    ...ActivityDialogTriggerFragment\n    __typename\n  }\n  dialogActions {\n    ...ActivityClickActionsFragment\n    __typename\n  }\n  __typename\n}\n\nfragment ActivityClickActionsFragment on ActivityClickAction {\n  accessibilityText\n  clientSideAnalytics {\n    linkName\n    referrerId\n    __typename\n  }\n  ... on ActivityLinkClickAction {\n    linkTagUrl\n    opensInNewTab\n    __typename\n  }\n  ... on ActivityRefClickAction {\n    sectionRef\n    __typename\n  }\n  ... on ActivitySelectionClickAction {\n    selectionList {\n      id\n      value\n      __typename\n    }\n    __typename\n  }\n  ... on ActivityPaginationInfoAction {\n    pagination {\n      size\n      startingIndex\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ActivityDialogTriggerFragment on ActivityDialogTrigger {\n  accessibility\n  analytics {\n    linkName\n    referrerId\n    __typename\n  }\n  ... on ActivityButtonDialogTrigger {\n    button {\n      ...EGDSButtonFragment\n      __typename\n    }\n    __typename\n  }\n  ... on ActivityGraphicDialogTrigger {\n    graphic {\n      ...EGDSGraphicFragment\n      __typename\n    }\n    __typename\n  }\n  ... on ActivityLinkDialogTrigger {\n    linkGraphic: graphic {\n      ...EGDSGraphicFragment\n      __typename\n    }\n    label\n    __typename\n  }\n  ... on ActivityFakeInputDialogTrigger {\n    icon {\n      id\n      __typename\n    }\n    label\n    value\n    __typename\n  }\n  ... on ActivityMapDialogTrigger {\n    staticMapImage {\n      accessibility\n      url\n      __typename\n    }\n    mapTriggerLabel: label\n    __typename\n  }\n  __typename\n}\n\nfragment EGDSButtonFragment on EGDSButton {\n  primary\n  accessibility\n  disabled\n  action {\n    ...EGDSButtonActionFragment\n    __typename\n  }\n  icon {\n    description\n    id\n    title\n    __typename\n  }\n  __typename\n}\n\nfragment EGDSButtonActionFragment on UIAction {\n  analytics {\n    linkName\n    referrerId\n    __typename\n  }\n  ... on ActivityOpenOffersModalAction {\n    activityId\n    dateRange {\n      startDate {\n        day\n        month\n        year\n        __typename\n      }\n      endDate {\n        day\n        month\n        year\n        __typename\n      }\n      __typename\n    }\n    dismissButtonAccessibility\n    dismissButtonAnalytics {\n      linkName\n      referrerId\n      __typename\n    }\n    selectedOffers {\n      offerProductNaturalKey\n      __typename\n    }\n    heading {\n      ...EGDSHeadingFragment\n      __typename\n    }\n    subHeading {\n      ...EGDSPlainTextFragment\n      __typename\n    }\n    __typename\n  }\n  ... on ActivityAddOfferToTripAction {\n    callbackMessages {\n      failure\n      success\n      __typename\n    }\n    offerNaturalKey {\n      offerProductNaturalKey\n      __typename\n    }\n    __typename\n  }\n  ... on ActivityRemoveOffersFromTripAction {\n    callbackMessages {\n      failure\n      success\n      __typename\n    }\n    offerNaturalKeys {\n      offerProductNaturalKey\n      __typename\n    }\n    __typename\n  }\n  ... on ActivityUpdateOfferInTripAction {\n    callbackMessages {\n      failure\n      success\n      __typename\n    }\n    newOfferNaturalKey {\n      offerProductNaturalKey\n      __typename\n    }\n    oldOfferNaturalKey {\n      offerProductNaturalKey\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment EGDSDialogFooterFragment on EGDSDialogFooter {\n  ... on EGDSInlineDialogFooter {\n    buttons {\n      ...EGDSDialogFooterButtonFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment EGDSDialogFooterButtonFragment on EGDSButton {\n  primary\n  accessibility\n  disabled\n  __typename\n}\n\nfragment ActivityReviewsSortTabFragment on ActivityTabbedNavigationBar {\n  heading\n  tabs {\n    label\n    selected\n    clickAction {\n      ...ActivityClickActionsFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ActivityReviewsMoreButtonFragment on ActivityReviewsPaginationButton {\n  action {\n    ...ActivityClickActionsFragment\n    __typename\n  }\n  button {\n    ...EGDSButtonFragment\n    __typename\n  }\n  __typename\n}\n',
    },
]

# type 2
PROPERTY_PAYLOAD = [
    {
        'operationName': 'PropertyFilteredReviewsQuery',
        'variables': {
            'context': {
                'siteId': 27,
                'locale': 'en_GB',
                'eapid': 0,
                'currency': 'INR',
                'device': {
                    'type': 'DESKTOP',
                },
                'identity': {
                    'duaid': 'ec7c1e1f-c76c-4de5-8b4b-8c565afdc8ed',
                    'expUserId': '-1',
                    'tuid': '-1',
                    'authState': 'ANONYMOUS',
                },
                'privacyTrackingState': 'CAN_TRACK',
                'debugContext': {
                    'abacusOverrides': [],
                    'alterMode': 'RELEASED',
                },
            },
            'propertyId': '976818',
            'searchCriteria': {
                'primary': {
                    'dateRange': None,
                    'rooms': [
                        {
                            'adults': 2,
                        },
                    ],
                    'destination': {
                        'regionId': '4925',
                    },
                },
                'secondary': {
                    'booleans': [
                        {
                            'id': 'includeRecentReviews',
                            'value': True,
                        },
                        {
                            'id': 'includeRatingsOnlyReviews',
                            'value': True,
                        },
                        {
                            'id': 'overrideEmbargoForIndividualReviews',
                            'value': True,
                        },
                    ],
                    'counts': [
                        {
                            'id': 'startIndex',
                            'value': 0,
                        },
                        {
                            'id': 'size',
                            'value': 100,
                        },
                    ],
                    'selections': [
                        {
                            'id': 'sortBy',
                            'value': 'NEWEST_TO_OLDEST_BY_LANGUAGE',
                        },
                        {
                            'id': 'searchTerm',
                            'value': '',
                        },
                    ],
                },
            },
        },
        'query': 'query PropertyFilteredReviewsQuery($context: ContextInput!, $propertyId: String!, $searchCriteria: PropertySearchCriteriaInput!) {\n  propertyReviewSummaries(\n    context: $context\n    propertyIds: [$propertyId]\n    searchCriteria: $searchCriteria\n  ) {\n    ...__PropertyReviewSummaryFragment\n    __typename\n  }\n  propertyInfo(context: $context, propertyId: $propertyId) {\n    id\n    reviewInfo(searchCriteria: $searchCriteria) {\n      ...__PropertyReviewsListFragment\n      sortAndFilter {\n        ...TravelerTypeFragment\n        ...SortTypeFragment\n        ...SearchTextFragment\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment __PropertyReviewSummaryFragment on PropertyReviewSummary {\n  accessibilityLabel\n  overallScoreWithDescriptionA11y {\n    ...LodgingEnrichedMessageFragment\n    __typename\n  }\n  propertyReviewCountDetails {\n    fullDescription\n    __typename\n  }\n  ...ReviewDisclaimerFragment\n  reviewSummaryDetails {\n    label\n    ratingPercentage\n    formattedRatingOutOfMax\n    __typename\n  }\n  totalCount {\n    raw\n    __typename\n  }\n  __typename\n}\n\nfragment ReviewDisclaimerFragment on PropertyReviewSummary {\n  reviewDisclaimer\n  reviewDisclaimerLabel\n  reviewDisclaimerAnalytics {\n    referrerId\n    linkName\n    __typename\n  }\n  reviewDisclaimerUrl {\n    value\n    accessibilityLabel\n    link {\n      url\n      __typename\n    }\n    __typename\n  }\n  reviewDisclaimerAccessibilityLabel\n  __typename\n}\n\nfragment LodgingEnrichedMessageFragment on LodgingEnrichedMessage {\n  __typename\n  subText\n  value\n  theme\n  state\n  accessibilityLabel\n  icon {\n    id\n    size\n    theme\n    __typename\n  }\n  mark {\n    id\n    __typename\n  }\n  egdsMark {\n    url {\n      value\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment __PropertyReviewsListFragment on PropertyReviews {\n  summary {\n    paginateAction {\n      text\n      analytics {\n        referrerId\n        linkName\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  reviews {\n    contentDirectFeedbackPromptId\n    ...ReviewParentFragment\n    managementResponses {\n      ...ReviewChildFragment\n      __typename\n    }\n    reviewInteractionSections {\n      primaryDisplayString\n      reviewInteractionType\n      __typename\n    }\n    __typename\n  }\n  ...NoResultsMessageFragment\n  __typename\n}\n\nfragment ReviewParentFragment on PropertyReview {\n  id\n  superlative\n  locale\n  title\n  brandType\n  reviewScoreWithDescription {\n    label\n    value\n    __typename\n  }\n  text\n  seeMoreAnalytics {\n    linkName\n    referrerId\n    __typename\n  }\n  submissionTime {\n    longDateFormat\n    __typename\n  }\n  impressionAnalytics {\n    event\n    referrerId\n    __typename\n  }\n  themes {\n    ...ReviewThemeFragment\n    __typename\n  }\n  reviewFooter {\n    ...PropertyReviewFooterSectionFragment\n    __typename\n  }\n  ...FeedbackIndicatorFragment\n  ...AuthorFragment\n  ...PhotosFragment\n  ...TravelersFragment\n  ...ReviewTranslationInfoFragment\n  ...PropertyReviewSourceFragment\n  ...PropertyReviewRegionFragment\n  __typename\n}\n\nfragment AuthorFragment on PropertyReview {\n  reviewAuthorAttribution {\n    text\n    __typename\n  }\n  __typename\n}\n\nfragment PhotosFragment on PropertyReview {\n  id\n  photoSection {\n    imageClickAnalytics {\n      referrerId\n      linkName\n      __typename\n    }\n    exitAnalytics {\n      referrerId\n      linkName\n      __typename\n    }\n    navClickAnalytics {\n      referrerId\n      linkName\n      __typename\n    }\n    __typename\n  }\n  photos {\n    description\n    url\n    __typename\n  }\n  __typename\n}\n\nfragment TravelersFragment on PropertyReview {\n  travelers\n  __typename\n}\n\nfragment ReviewThemeFragment on ReviewThemes {\n  icon {\n    id\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment FeedbackIndicatorFragment on PropertyReview {\n  reviewInteractionSections {\n    primaryDisplayString\n    accessibilityLabel\n    reviewInteractionType\n    feedbackAnalytics {\n      linkName\n      referrerId\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ReviewTranslationInfoFragment on PropertyReview {\n  translationInfo {\n    loadingTranslationText\n    targetLocale\n    translatedBy {\n      description\n      __typename\n    }\n    translationCallToActionLabel\n    seeOriginalText\n    __typename\n  }\n  __typename\n}\n\nfragment PropertyReviewSourceFragment on PropertyReview {\n  propertyReviewSource {\n    accessibilityLabel\n    graphic {\n      description\n      id\n      size\n      token\n      url {\n        value\n        __typename\n      }\n      __typename\n    }\n    text {\n      value\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PropertyReviewRegionFragment on PropertyReview {\n  reviewRegion {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment PropertyReviewFooterSectionFragment on PropertyReviewFooterSection {\n  messages {\n    seoStructuredData {\n      itemscope\n      itemprop\n      itemtype\n      content\n      __typename\n    }\n    text {\n      ... on EGDSPlainText {\n        text\n        __typename\n      }\n      ... on EGDSGraphicText {\n        text\n        graphic {\n          ... on Mark {\n            description\n            id\n            size\n            url {\n              ... on HttpURI {\n                relativePath\n                value\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ReviewChildFragment on ManagementResponse {\n  id\n  header {\n    text\n    __typename\n  }\n  response\n  __typename\n}\n\nfragment NoResultsMessageFragment on PropertyReviews {\n  noResultsMessage {\n    __typename\n    ...MessagingCardFragment\n    ...EmptyStateFragment\n  }\n  __typename\n}\n\nfragment MessagingCardFragment on UIMessagingCard {\n  graphic {\n    __typename\n    ... on Icon {\n      id\n      description\n      __typename\n    }\n  }\n  primary\n  secondaries\n  __typename\n}\n\nfragment EmptyStateFragment on UIEmptyState {\n  heading\n  body\n  __typename\n}\n\nfragment TravelerTypeFragment on SortAndFilterViewModel {\n  sortAndFilter {\n    name\n    label\n    options {\n      label\n      isSelected\n      optionValue\n      description\n      clickAnalytics {\n        linkName\n        referrerId\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SortTypeFragment on SortAndFilterViewModel {\n  sortAndFilter {\n    name\n    label\n    clickAnalytics {\n      linkName\n      referrerId\n      __typename\n    }\n    options {\n      label\n      isSelected\n      optionValue\n      description\n      clickAnalytics {\n        linkName\n        referrerId\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SearchTextFragment on SortAndFilterViewModel {\n  sortAndFilter {\n    name\n    label\n    graphic {\n      ... on Icon {\n        description\n        id\n        token\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n',
    },
]
