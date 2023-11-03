from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from api.views import setting_views, dashboard_views, report_views, export_views, client_views, user_views, \
    stream_views, notification_views, schedule_views, stripe_views, webhooks, generic, paypal_views, report_export_views, stream_names_views, trending_views
router = DefaultRouter()

router.register(r'settings/timezone', setting_views.UserTimezoneViewSet, basename='settings-timezone')
router.register(r'settings/standard-email-address', setting_views.StandardCopyEmailAddressViewSet, basename='settings-standard-email-address')
router.register(r'clients', client_views.ClientViewSet, basename='clients')
router.register(r'users', user_views.UserViewSet, basename='users')
router.register(r'urlstreams', stream_views.UrlStreamViewSet, basename='urlstreams')
router.register(r'credentialstreams', stream_views.CredentialStreamViewSet, basename='credentialstreams')
router.register(r'apikeystreams', stream_views.ApiKeyStreamViewSet, basename='apikeystreams')
router.register(r'exportschedules', schedule_views.ExportScheduleViewSet, basename='exportschedules')
router.register(r'schedule-email', schedule_views.ScheduleEmailAddressViewSet, basename='schedule-email')
router.register(r'notifications', notification_views.NotificationViewSet, basename='notifications')
router.register(r'streamnames', stream_names_views.StreamNameViewSet, basename='streamnames')
# router.register(r'streamnames/update', stream_names_views.StreamNamesUpdateViewSet, basename='streamnames')


urlpatterns = [
    path('', include(router.urls)),
    path('reviews-totals/', dashboard_views.ReviewsTotalsAPIView.as_view(), name='reviews-totals'),
    path('reviews/', dashboard_views.ReviewListAPIView.as_view(), name='reviews'),
    path('pending-reviews/', dashboard_views.PendingReviewViewSet.as_view(), name='pending-reviews'),
    path('check-sync/<int:review_id>/', dashboard_views.CheckSyncAPIView.as_view(), name='check-sync'),
    path('agencies/', setting_views.AgencyStreamView.as_view(), name='agencies'),
    path('respond-to-review/', dashboard_views.RespondToReview.as_view(), name='respond-to-review'),
    path('comparative-graphics/', report_views.ComparativeGraphicsAPIView.as_view(), name='comparative-graphics'),
    path('reviews-location/', report_views.ReviewsLocationAPIView.as_view(), name='reviews-location'),
    path('summary-evolution/', report_views.SummaryEvolutionAPIView.as_view(), name='summary-evolution'),
    path('summary-evolution-totals/', report_views.SummaryEvolutionTotalsAPIView.as_view(), name='summary-evolution-totals'),
    path('reputation/', report_views.ReputationAPIView.as_view(), name='reputation'),
    path('keywords/', report_views.KeywordAPIView.as_view(), name='keywords'),
    path('tours/', setting_views.ToursView.as_view(), name='tours'),
    path('countries/', setting_views.CountryList.as_view(), name='contries'),
    path('cities/', setting_views.CityList.as_view(), name='cities'),
    path('export-xlsx/', export_views.ExportAPIView.as_view(), name='export-xlsx'),
    path('export-pdf/', export_views.ExportPDFAPIView.as_view(), name='export-pdf'),
    path('clients/<int:pk>/reset-password/', client_views.ClientPasswordResetView.as_view(), name='client-reset-password'),
    path('users/<int:pk>/reset-password/', user_views.UserPasswordResetView.as_view(), name='user-reset-password'),
    path('template/<int:stream_type>/', stream_views.StreamTemplateView.as_view()),
    path('stream-max/', stream_views.StreamMaxView.as_view()),
    path('create-notification/', notification_views.CreateNotificationView.as_view()),
    path('update-notification/<int:pk>/', notification_views.UpdateNotificationView.as_view()),
    path('delete-notification/<int:pk>/', notification_views.DeleteNotificationView.as_view()),

    path('export-comparative-graphics/', report_export_views.ExportComparativeGraphicsAPIView.as_view(), name='export-comparative-graphics'),
    path('export-reviews-location/', report_export_views.ExportReviewsLocationAPIView.as_view(), name='export-reviews-location'),
    path('export-summary-evolution/', report_export_views.ExportSummaryEvolutionAPIView.as_view(), name='export-summary-evolution'),
    path('export-reputation/', report_export_views.ExportReputationAPIView.as_view(), name='export-reputation'),
    path('export-keywords/', report_export_views.ExportKeywordAPIView.as_view(), name='export-keywords'),

    path('hello/', generic.HelloView.as_view(), name='hello'),
    path('success/', generic.ExampleSuccessView.as_view(), name='success'),
    path('cancel/', generic.ExampleCancelView.as_view(), name='cancel'),
    path('costs/', generic.CostsView.as_view(), name='costs'),

    # Stripe
    path('stripe-config/', stripe_views.stripe_config),
    path('create-stripe-checkout-session/', stripe_views.CreateCheckoutSessionView.as_view(), name='create-stripe-checkout-session'),
    path('delete-subscription/', stripe_views.DeleteSubscriptionView.as_view(), name='delete-subscription'),
    path('upgrade-subscription/', stripe_views.UpgradeSubscriptionView.as_view(), name='upgrade-subscription'),
    path('webhook/stripe/', webhooks.stripe_webhook, name="webhook-stripe"),


    path('paypal-config/', paypal_views.paypal_config, name='paypal_config'),
    path('create-paypal-checkout-session/', paypal_views.CreateCheckoutSessionView.as_view(), name='create_paypal_checkout_session'),
    path('webhook/paypal/', webhooks.paypal_webhook, name="webhook-paypal"),

    path('update-streamnames/', stream_names_views.StreamNamesUpdateViewSet.as_view(), name='stream-name-update'),

    path('trending/',trending_views.TrendingViewset.as_view(), name = 'trending' ),
    path('trending-keywords/', trending_views.TrendingKeywordsViewset.as_view(), name='trending-keywords'),
]