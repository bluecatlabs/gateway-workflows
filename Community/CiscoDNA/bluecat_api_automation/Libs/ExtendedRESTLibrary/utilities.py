class CompareLists:
    @staticmethod
    def compare_two_lists(actual_list, expected_list):
        for key in actual_list:
            if key in expected_list:
                if actual_list[key] != expected_list[key]:
                    msg = "For %s field, actual %s  value is not matching with expected %s value" % (key, actual_list[key], expected_list[key])
                    raise AssertionError(msg)
            else:
                msg = "There is no %s field in the expected file" % key
                raise AssertionError(msg)
        return True

# class CompareFiles:
#     @staticmethod
#     def compare_two_file(f1, f2):
#         # bufsize = BUFSIZE
#         with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
#             while True:
#                 b1 = fp1.read()
#                 print(b1)
#                 b2 = fp2.read()
#                 print(b2)
#                 if b1 != b2:
#                     return False
#                 else:
#                     return True
