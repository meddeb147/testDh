import 'package:aziz_s_application1/core/app_export.dart';
import 'package:aziz_s_application1/presentation/phone_verification_screen/models/phone_verification_model.dart';

class PhoneVerificationController extends GetxController {
  Rx<PhoneVerificationModel> phoneVerificationModelObj =
      PhoneVerificationModel().obs;

  @override
  void onReady() {
    super.onReady();
  }

  @override
  void onClose() {
    super.onClose();
  }
}
