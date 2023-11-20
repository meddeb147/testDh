import 'package:aziz_s_application1/core/app_export.dart';
import 'package:aziz_s_application1/presentation/two_factor_authentication_screen/models/two_factor_authentication_model.dart';

class TwoFactorAuthenticationController extends GetxController {
  Rx<TwoFactorAuthenticationModel> twoFactorAuthenticationModelObj =
      TwoFactorAuthenticationModel().obs;

  @override
  void onReady() {
    super.onReady();
    Future.delayed(const Duration(milliseconds: 3000), () {
      Get.offNamed(
        AppRoutes.phoneVerificationScreen,
      );
    });
  }

  @override
  void onClose() {
    super.onClose();
  }
}
