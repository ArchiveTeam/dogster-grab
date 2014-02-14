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

* thread:NNNN to download `http://www.dogster.com/forums/thread_url.php?thread_id=486467`

Proposed:

* forums:NNNN to download `???` to get http://www.dogster.com/forums/group/321196

* answers-dogster:SSSS to download `http://www.dogster.com/answers/question/my_dog_is_having_a_phantom_pregnancy_and_im_wondering_if_i_should_take_the_toy_shes_nesting_away_als-98178`
* answers-catster:SSSS see above
