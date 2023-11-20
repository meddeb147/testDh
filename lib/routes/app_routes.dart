import 'package:aziz_s_application1/presentation/account_creation_screen/account_creation_screen.dart';
import 'package:aziz_s_application1/presentation/account_creation_screen/binding/account_creation_binding.dart';
import 'package:aziz_s_application1/presentation/password_encryption_screen/password_encryption_screen.dart';
import 'package:aziz_s_application1/presentation/password_encryption_screen/binding/password_encryption_binding.dart';
import 'package:aziz_s_application1/presentation/phone_verification_screen/phone_verification_screen.dart';
import 'package:aziz_s_application1/presentation/phone_verification_screen/binding/phone_verification_binding.dart';
import 'package:aziz_s_application1/presentation/edit_profile_screen/edit_profile_screen.dart';
import 'package:aziz_s_application1/presentation/edit_profile_screen/binding/edit_profile_binding.dart';
import 'package:aziz_s_application1/presentation/security_policy_screen/security_policy_screen.dart';
import 'package:aziz_s_application1/presentation/security_policy_screen/binding/security_policy_binding.dart';
import 'package:aziz_s_application1/presentation/sign_up_screen/sign_up_screen.dart';
import 'package:aziz_s_application1/presentation/sign_up_screen/binding/sign_up_binding.dart';
import 'package:aziz_s_application1/presentation/signup_login_module_screen/signup_login_module_screen.dart';
import 'package:aziz_s_application1/presentation/signup_login_module_screen/binding/signup_login_module_binding.dart';
import 'package:aziz_s_application1/presentation/splash_screen/splash_screen.dart';
import 'package:aziz_s_application1/presentation/splash_screen/binding/splash_binding.dart';
import 'package:aziz_s_application1/presentation/terms_and_conditions_screen/terms_and_conditions_screen.dart';
import 'package:aziz_s_application1/presentation/terms_and_conditions_screen/binding/terms_and_conditions_binding.dart';
import 'package:aziz_s_application1/presentation/two_factor_authentication_screen/two_factor_authentication_screen.dart';
import 'package:aziz_s_application1/presentation/two_factor_authentication_screen/binding/two_factor_authentication_binding.dart';
import 'package:aziz_s_application1/presentation/app_navigation_screen/app_navigation_screen.dart';
import 'package:aziz_s_application1/presentation/app_navigation_screen/binding/app_navigation_binding.dart';
import 'package:get/get.dart';

class AppRoutes {
  static const String accountCreationScreen = '/account_creation_screen';

  static const String passwordEncryptionScreen = '/password_encryption_screen';

  static const String phoneVerificationScreen = '/phone_verification_screen';

  static const String editProfileScreen = '/edit_profile_screen';

  static const String securityPolicyScreen = '/security_policy_screen';

  static const String signUpScreen = '/sign_up_screen';

  static const String signupLoginModuleScreen = '/signup_login_module_screen';

  static const String splashScreen = '/splash_screen';

  static const String termsAndConditionsScreen = '/terms_and_conditions_screen';

  static const String twoFactorAuthenticationScreen =
      '/two_factor_authentication_screen';

  static const String appNavigationScreen = '/app_navigation_screen';

  static const String initialRoute = '/initialRoute';

  static List<GetPage> pages = [
    GetPage(
      name: accountCreationScreen,
      page: () => AccountCreationScreen(),
      bindings: [
        AccountCreationBinding(),
      ],
    ),
    GetPage(
      name: passwordEncryptionScreen,
      page: () => PasswordEncryptionScreen(),
      bindings: [
        PasswordEncryptionBinding(),
      ],
    ),
    GetPage(
      name: phoneVerificationScreen,
      page: () => PhoneVerificationScreen(),
      bindings: [
        PhoneVerificationBinding(),
      ],
    ),
    GetPage(
      name: editProfileScreen,
      page: () => EditProfileScreen(),
      bindings: [
        EditProfileBinding(),
      ],
    ),
    GetPage(
      name: securityPolicyScreen,
      page: () => SecurityPolicyScreen(),
      bindings: [
        SecurityPolicyBinding(),
      ],
    ),
    GetPage(
      name: signUpScreen,
      page: () => SignUpScreen(),
      bindings: [
        SignUpBinding(),
      ],
    ),
    GetPage(
      name: signupLoginModuleScreen,
      page: () => SignupLoginModuleScreen(),
      bindings: [
        SignupLoginModuleBinding(),
      ],
    ),
    GetPage(
      name: splashScreen,
      page: () => SplashScreen(),
      bindings: [
        SplashBinding(),
      ],
    ),
    GetPage(
      name: termsAndConditionsScreen,
      page: () => TermsAndConditionsScreen(),
      bindings: [
        TermsAndConditionsBinding(),
      ],
    ),
    GetPage(
      name: twoFactorAuthenticationScreen,
      page: () => TwoFactorAuthenticationScreen(),
      bindings: [
        TwoFactorAuthenticationBinding(),
      ],
    ),
    GetPage(
      name: appNavigationScreen,
      page: () => AppNavigationScreen(),
      bindings: [
        AppNavigationBinding(),
      ],
    ),
    GetPage(
      name: initialRoute,
      page: () => TwoFactorAuthenticationScreen(),
      bindings: [
        TwoFactorAuthenticationBinding(),
      ],
    )
  ];
}
