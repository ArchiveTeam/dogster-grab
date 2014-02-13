Dev notes
=========

Item names
==========

The pipeline expects items name formatted as TYPE:DATA.

The pipeline currently supports

* profile:NNNN (e.g profile:851925) which will download http://www.dogster.com/dogs/851925 and http://www.catster.com/cats/851925

* group-page:NNNN to download single page of http://www.dogster.com/group/grp_page.php?g=8835 (including the redirect to the canonical url)
* group-messages:NNNN to download `http://www.dogster.com/group/grp_message_list.php?g=8835`
* group-events:NNNN to download `http://www.dogster.com/group/grp_event_list.php?g=8835`
* group-links:NNNN to download `http://www.dogster.com/group/grp_link_list.php?g=8835`
* group-members:NNNN to download `http://www.dogster.com/group/grp_member_list.php?g=8835`

Proposed:

* forums-group:NNNN to download http://www.dogster.com/forums/group/321196 (listings only)
* thread-group:NNNN to download http://www.dogster.com/forums/group/thread/486467

* thread-dogster:SSSS to download  `http://www.dogster.com/forums/When_its_Time_to_Say_Goodbye/thread/799482` (SSSS is `When_its_Time_to_Say_Goodbye/thread/799482`)
* thread-catster:SSSS see above.

* answers-dogster:SSSS to download `http://www.dogster.com/answers/question/my_dog_is_having_a_phantom_pregnancy_and_im_wondering_if_i_should_take_the_toy_shes_nesting_away_als-98178`
* answers-catster:SSSS see above
